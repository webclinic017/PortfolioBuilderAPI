import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_fund_response_code():
    response = client.post(
        "/backtest/",
        json={
            "start_date": "2018-12-31",
            "end_date": "2020-01-30",
            "portfolio": [
                {"fund": "F00000UEXJ", "amount": 1000},
            ],
            "strategy": {"rebalance": True, "rebalance_frequency": "Y"},
        },
    )
    assert response.status_code == 200


def test_fund_response_backtest_rebalancefalse():
    response = client.post(
        "/backtest/",
        json={
            "start_date": "2018-12-31",
            "end_date": "2020-01-30",
            "portfolio": [
                {"fund": "F00000UEXJ", "amount": 1000},
                {"fund": "F00000OJMA", "amount": 1000},
            ],
            "strategy": {"rebalance": False, "rebalance_frequency": "Y"},
        },
    )
    assert response.json()["projection"][0]["portfolio"] == 2000
    assert response.json()["projection"][0]["drawdown"] == 0
    assert response.json()["projection"][0]["date"] == "2018-12-31"

    assert response.json()["projection"][-1]["portfolio"] == pytest.approx(
        2467.0695460478
    )
    assert response.json()["projection"][-1]["drawdown"] == pytest.approx(
        -0.0294445297
    )
    assert response.json()["projection"][-1]["date"] == "2020-01-30"


def test_fund_response_backtest_rebalancetrue():
    response = client.post(
        "/backtest/",
        json={
            "start_date": "2018-12-31",
            "end_date": "2020-01-30",
            "portfolio": [
                {"fund": "F00000UEXJ", "amount": 1000},
                {"fund": "F00000OJMA", "amount": 1000},
            ],
            "strategy": {"rebalance": True, "rebalance_frequency": "Y"},
        },
    )

    assert response.json()["projection"][0]["portfolio"] == 2000
    assert response.json()["projection"][0]["drawdown"] == 0
    assert response.json()["projection"][0]["date"] == "2018-12-31"

    assert response.json()["projection"][-1]["portfolio"] == pytest.approx(
        2465.5738044157
    )
    assert response.json()["projection"][-1]["drawdown"] == pytest.approx(
        -0.0294748496
    )
    assert response.json()["projection"][-1]["date"] == "2020-01-30"

    assert response.json()["metrics"]["metrics"]["cagr"] == pytest.approx(
        0.21350801373437478
    )
    assert response.json()["metrics"]["metrics"]["std_m"] == pytest.approx(
        0.027241926252289553
    )
    assert response.json()["metrics"]["metrics"][
        "std_downside_m"
    ] == pytest.approx(0.005651932970421152)
    assert response.json()["metrics"]["metrics"][
        "sharpe_ratio"
    ] == pytest.approx(7.470397351849188)
    assert response.json()["metrics"]["metrics"][
        "sortino_ratio"
    ] == pytest.approx(36.006798877377776)
    assert response.json()["metrics"]["metrics"][
        "max_drawdown"
    ] == pytest.approx(0.06304792760097977)
