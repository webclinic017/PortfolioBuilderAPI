import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_frontier_response_code():
    response = client.post(
        "/optimisation/",
        json={
            "start_date": "2015-12-31",
            "end_date": "2019-12-31",
            "funds": ["AAPL", "AMZN"],
            "num_portfolios": 2,
        },
    )
    assert response.status_code == 200


def test_frontier_three_funds():
    response = client.post(
        "/optimisation/",
        json={
            "start_date": "2015-12-31",
            "end_date": "2019-12-31",
            "funds": ["AAPL", "AMZN", "AMD"],
            "num_portfolios": 4,
        },
    )
    assert response.json()["frontier"][0]["returns"] == 0.074789
    assert response.json()["frontier"][0]["std"] == 0.176781
    assert response.json()["frontier"][0]["portfolio_weights"]["AMD"] == 1
    assert response.json()["frontier"][1]["returns"] == 0.057992
    assert response.json()["frontier"][1]["std"] == 0.126705
    assert response.json()["frontier"][1]["portfolio_weights"]["AAPL"] == 0.345962
