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
            "funds": ["F00000UEXJ", "F00000OOB2"],
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
            "funds": ["F00000UEXJ", "F00000OJMA", "F00000OOB2"],
            "num_portfolios": 4,
        },
    )
    assert response.json()["frontier"][0]["returns"] == pytest.approx(0.013781)
    assert response.json()["frontier"][0]["std"] == pytest.approx(0.035669)
    assert (
        response.json()["frontier"][0]["portfolio_weights"]["F00000OJMA"] == 1
    )
    assert response.json()["frontier"][1]["returns"] == pytest.approx(0.011762)
    assert response.json()["frontier"][1]["std"] == pytest.approx(0.030697)
    assert response.json()["frontier"][1]["portfolio_weights"][
        "F00000UEXJ"
    ] == pytest.approx(0.142057)
