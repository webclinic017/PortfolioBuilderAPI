from typing import Dict

import numpy as np
from fastapi import APIRouter

from src import schemas
from src.modules.data_loader import DataLoader
from src.modules.optimisation import PortfolioOptimisation

router = APIRouter()


@router.post("/", tags=["Portfolio Optimisation"])
def efficient_frontier(item: schemas.optimisation) -> Dict:
    """
    Request efficient frontier

    Args:
        item (schemas.optimisation): Input request for optimisation

    Returns:
        Dict: Portfolios that lie on efficient frontier
    """
    fund_codes = item.dict()["funds"]
    start_date = item.dict()["start_date"]
    end_date = item.dict()["end_date"]
    num_portfolios = item.dict()["num_portfolios"]
    frequency = "monthly"
    historical_returns = DataLoader().load_historical_returns(
        fund_codes=fund_codes,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
    )
    risk_free = DataLoader().load_ff_factors(
        regression_factors=[],
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
    )["RF"]
    average_risk_free = np.mean(risk_free)
    fund_returns = np.mean(historical_returns.drop(columns=["date"]))
    fund_covariance = historical_returns.drop(columns=["date"]).cov()
    frontier = PortfolioOptimisation().efficient_frontier(
        fund_returns,
        fund_covariance,
        num_portfolios,
        fund_codes,
        average_risk_free,
    )
    result = {}
    result["frontier"] = frontier
    ticker_summary = []
    for i in fund_codes:
        ticker = {}
        ticker["ticker"] = i
        ticker["returns"] = np.mean(historical_returns[i])
        ticker["std"] = historical_returns[i].std()

        ticker_summary.append(ticker)
    result["tickers"] = ticker_summary
    return result
