import json
from typing import Any, List

import numpy as np
import pandas as pd
from pydantic import BaseModel
from scipy.optimize import minimize


def portfolio_std(weights: List, fund_covariance: pd.DataFrame) -> float:
    """
    Calculate portfolio standard deviation using covariance

    Args:
        weights (List): fund weights
        fund_covariance (pd.DataFrame): fund covariance

    Returns:
        float: portfolio std

    """
    weights = np.array(weights)
    std = np.sqrt(np.dot(weights.T, np.dot(fund_covariance, weights)))
    return std


class PortfolioOptimisation(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    def portfolio_return(
        self, weights: List[float], fund_returns: pd.Series
    ) -> float:
        """
        Calculate arithmetic return of a portfolio

        Args:
            weights (List[float]): portfolio weights
            fund_returns (pd.Series): Returns for each ticker

        Returns:
            float: Portfolio Return
        """
        annualised_return = np.sum(fund_returns * weights)
        return annualised_return

    def optimise_std(
        self,
        fund_returns: pd.Series,
        fund_covariance: pd.DataFrame,
        target: float,
    ) -> List[float]:
        """
        Use optimisation to find portfolio with minimum std for a given return

        Args:
            fund_returns (pd.Series): Returns for each ticker
            fund_covariance (pd.DataFrame): Covariance between each ticker
            target (float): Target return

        Returns:
            List[float]: Optimised portfolio weight
        """
        args = fund_covariance
        num_funds = len(fund_returns)

        def portfolio_return(weights):
            annualised_return = np.sum(fund_returns * weights)
            return annualised_return

        constraints = (
            {"type": "eq", "fun": lambda x: portfolio_return(x) - target},
            {"type": "eq", "fun": lambda x: np.sum(x) - 1},
        )
        bounds = tuple((0, 1) for i in range(num_funds))
        initial_weights = num_funds * [
            1.0 / num_funds,
        ]
        result = minimize(
            portfolio_std,
            initial_weights,
            args=args,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        ).x
        result = [round(elem, 6) for elem in result]
        return result

    def efficient_frontier_portfolios(
        self,
        fund_returns: pd.Series,
        fund_covariance: pd.DataFrame,
        portfolios: int,
    ) -> List:
        """
        Find range of portfolios that lie on the efficient frontier

        Args:
            fund_returns (pd.Series): Returns for each ticker
            fund_covariance (pd.DataFrame): Covariance between each ticker
            portfolios (int): Number of portfolios to generate

        Returns:
            List: Portfolios that lie on the efficient frontier
        """
        return_range = (fund_returns.max() - fund_returns.min()) / (
            portfolios - 1
        )
        efficient_range = []
        for i in range(portfolios):
            efficient_range.append(fund_returns.min() + return_range * i)
        efficient_portfolios = []
        for j in efficient_range:
            efficient_portfolios.append(
                self.optimise_std(fund_returns, fund_covariance, j)
            )
        return efficient_portfolios

    def efficient_frontier(
        self,
        fund_returns: pd.Series,
        fund_covariance: pd.DataFrame,
        portfolios: pd.DataFrame,
        fund_codes: List[str],
        average_risk_free: float,
    ) -> Any:
        """
        Get range of portfolios that lie on the efficient frontier and summary statistics

        Args:
            fund_returns (pd.Series): Returns for each ticker
            fund_covariance (pd.DataFrame): Covariance between each ticker
            portfolios (int): Number of portfolios to generate
            fund_codes (List[str]): Tickers to include
            average_risk_free (float): Risk free for given period of returns

        Returns:
            Any: json like object that contains range of portfolios
        """
        efficient_portfolios = self.efficient_frontier_portfolios(
            fund_returns, fund_covariance, portfolios
        )
        result = []
        for i in efficient_portfolios:
            portfolio_weights = {}
            for j in range(len(fund_codes)):
                portfolio_weights[fund_codes[j]] = i[j]
            portfolio_stats = {
                "portfolio_weights": portfolio_weights,
                "returns": round(self.portfolio_return(i, fund_returns), 6),
                "std": round(portfolio_std(i, fund_covariance), 6),
            }
            portfolio_stats["sharpe_ratio"] = (
                portfolio_stats["returns"] - average_risk_free
            ) / portfolio_stats["std"]
            result.append(portfolio_stats)
        result = (
            pd.DataFrame(result)
            .sort_values(by="returns", ascending=False)
            .reset_index(drop=True)
        )
        idx = result[["std"]].idxmin()[0]
        result = result.iloc[0:idx]
        return json.loads(result.to_json(orient="records"))
