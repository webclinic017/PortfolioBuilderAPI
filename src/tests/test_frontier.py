import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_frontier_response_code():
    response = client.post(
        "/portfolioOptimisation/",
        json={
            "startDate": "2017-12-31",
            "endDate": "2018-12-31",
            "funds": ["AAPL", "AMZN"],
            "numberOfPortfolios": 3,
        },
    )
    assert response.status_code == 200


def test_frontier_three_funds():
    response = client.post(
        "/portfolioOptimisation/",
        json={
            "startDate": "2015-12-31",
            "endDate": "2018-12-31",
            "funds": ["AAPL", "AMZN", "AMD"],
            "numberOfPortfolios": 3,
        },
    )
    assert response.json()[0]["returns"] == 0.015968
    assert response.json()[0]["std"] == 0.080849
    assert response.json()[0]["portfolioWeights"]["AAPL"] == 1
    assert response.json()[1]["returns"] == 0.043716
    assert response.json()[1]["std"] == 0.109745
    assert response.json()[1]["portfolioWeights"]["AMZN"] == 0.434734
    assert response.json()[2]["returns"] == 0.071464
    assert response.json()[2]["std"] == 0.194115
