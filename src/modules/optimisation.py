import json
from typing import TypeVar

import numpy as np
import pandas as pd
from pydantic import BaseModel
from scipy.optimize import minimize

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")


def portfolio_std(weights, fund_covariance):
    weights = np.array(weights)
    std = np.sqrt(np.dot(weights.T, np.dot(fund_covariance, weights)))
    return std


class PortfolioOptimisation(BaseModel):
    def portfolio_return(self, weights, fund_returns):
        annualised_return = np.sum(fund_returns * weights)

        return annualised_return

    def optimise_std(self, fund_returns, fund_covariance, target):
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

    def efficient_frontier_portfolios(self, fund_returns, fund_covariance, portfolios):
        return_range = (fund_returns.max() - fund_returns.min()) / (portfolios - 1)
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
        self, fund_returns, fund_covariance, portfolios, fund_codes, average_risk_free
    ):

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
