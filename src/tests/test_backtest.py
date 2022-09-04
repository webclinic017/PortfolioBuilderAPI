import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_fund_response_code():
    response = client.post(
        "/backtest/",
        json={
            "startDate": "2018-12-31",
            "endDate": "2019-01-31",
            "portfolio": [
                {"fund": "ABMD", "amount": 1000},
            ],
            "strategy": {"rebalance": False, "rebalanceFrequency": "Y"},
        },
    )
    assert response.status_code == 200


def test_fund_response_backtest_rebalancefalse():
    response = client.post(
        "/backtest/",
        json={
            "startDate": "2018-12-31",
            "endDate": "2020-01-31",
            "portfolio": [
                {"fund": "ABMD", "amount": 1000},
                {"fund": "ATVI", "amount": 1000},
            ],
            "strategy": {"rebalance": False, "rebalanceFrequency": "Y"},
        },
    )
    assert response.json()["projection"][0] == {
        "portfolio": 2000,
        "drawdown": 0,
        "date": "2018-12-31",
    }

    assert response.json()["projection"][-1] == {
        "portfolio": 1839.0805606,
        "drawdown": -0.1380724721,
        "date": "2020-01-31",
    }


def test_fund_response_backtest_rebalancetrue():
    response = client.post(
        "/backtest/",
        json={
            "startDate": "2018-12-31",
            "endDate": "2020-01-31",
            "portfolio": [
                {"fund": "ABMD", "amount": 1000},
                {"fund": "ATVI", "amount": 1000},
            ],
            "strategy": {"rebalance": True, "rebalanceFrequency": "Y"},
        },
    )
    assert response.json()["projection"][0] == {
        "portfolio": 2000,
        "drawdown": 0,
        "date": "2018-12-31",
    }

    assert response.json()["projection"][-1] == {
        "portfolio": 1919.845369844,
        "drawdown": -0.1002201812,
        "date": "2020-01-30",
    }


def test_fund_response_backtest_rebalancetrue():
    response = client.post(
        "/backtest/",
        json={
            "startDate": "2018-12-31",
            "endDate": "2020-01-31",
            "portfolio": [
                {"fund": "ABMD", "amount": 1000},
                {"fund": "ATVI", "amount": 1000},
            ],
            "strategy": {"rebalance": True, "rebalanceFrequency": "M"},
        },
    )
    assert response.json()["projection"][0] == {
        "portfolio": 2000,
        "drawdown": 0,
        "date": "2018-12-31",
    }

    assert response.json()["projection"][-1] == {
        "portfolio": 1818.823022723,
        "drawdown": -0.1475666345,
        "date": "2020-01-30",
    }

    assert response.json()["metrics"]["cagr"] == -0.0840611838635632

    assert response.json()["metrics"]["monthly_std"] == 0.065807084997883

    assert response.json()["metrics"]["downside_std"] == 0.04167162496914203

    assert response.json()["metrics"]["sharpe_ratio"] == -1.429347369916007

    assert response.json()["metrics"]["sortino_ratio"] == -2.2571998076200726

    assert response.json()["metrics"]["max_drawdown"] == -0.2728276516

    assert (
        response.json()["metrics"]["monthlyReturns"][0]["monthlyReturn"] == 0.0472346979
    )
