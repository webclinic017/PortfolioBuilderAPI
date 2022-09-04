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
                {"fund": "ABMD", "amount": 1000},
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
                {"fund": "ABMD", "amount": 1000},
                {"fund": "ATVI", "amount": 1000},
            ],
            "strategy": {"rebalance": False, "rebalance_frequency": "Y"},
        },
    )
    assert response.json()["projection"][0]["portfolio"] == 2000
    assert response.json()["projection"][0]["drawdown"] == 0
    assert response.json()["projection"][0]["date"] == "2018-12-31"

    assert response.json()["projection"][-1]["portfolio"] == 1892.9741188256
    assert response.json()["projection"][-1]["drawdown"] == -0.1128140128
    assert response.json()["projection"][-1]["date"] == "2020-01-30"


def test_fund_response_backtest_rebalancetrue():
    response = client.post(
        "/backtest/",
        json={
            "start_date": "2018-12-31",
            "end_date": "2020-01-30",
            "portfolio": [
                {"fund": "ABMD", "amount": 1000},
                {"fund": "ATVI", "amount": 1000},
            ],
            "strategy": {"rebalance": True, "rebalance_frequency": "Y"},
        },
    )

    assert response.json()["projection"][0]["portfolio"] == 2000
    assert response.json()["projection"][0]["drawdown"] == 0
    assert response.json()["projection"][0]["date"] == "2018-12-31"

    assert response.json()["projection"][-1]["portfolio"] == pytest.approx(
        1919.845369844
    )
    assert response.json()["projection"][-1]["drawdown"] == -0.1002201812
    assert response.json()["projection"][-1]["date"] == "2020-01-30"

    assert response.json()["metrics"]["metrics"]["cagr"] == -0.03711558507809487
    assert response.json()["metrics"]["metrics"]["std_m"] == 0.0630209788643494
    assert (
        response.json()["metrics"]["metrics"]["std_downside_m"] == 0.03288779681091077
    )
    assert response.json()["metrics"]["metrics"]["sharpe_ratio"] == -0.7476174748016788
    assert response.json()["metrics"]["metrics"]["sortino_ratio"] == -1.4326160353333224
    assert response.json()["metrics"]["metrics"]["max_drawdown"] == 0.2666609975147659
