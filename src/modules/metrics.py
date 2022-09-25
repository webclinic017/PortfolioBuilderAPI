import json
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from pydantic import BaseModel


class Metrics(BaseModel):
    def returns(self, series: pd.Series) -> pd.Series:
        """
        Calculate returns for a given series

        Args:
            series (pd.Series): Series for index / ticker

        Returns:
            pd.Series: Return after each period
        """
        return (series / series.shift(periods=1)) - 1

    def std(self, series: pd.Series) -> float:
        """Calculate the standard deviation for a given series

        Args:
            series (pd.Series): Ticker Returns

        Returns:
            float: standard deviation
        """
        if len(series) < 2:
            result = 0
        else:
            result = np.std(series)
        return result

    def geometric_mean(self, series: np.array) -> float:
        """
        Calculate geometric mean of a given series

        Args:
            series (np.array): Series of returns

        Returns:
            float: Geometric mean
        """
        return np.power(np.prod(series + 1.0), 1 / len(series)) - 1.0

    def annualise_returns(self, value: float) -> float:
        """
        Annualise monthly returns

        Args:
            value (float): Monthly return

        Returns:
            float: Annual return
        """
        return np.power(1 + value, 12) - 1

    def cagr(self, series: pd.Series, dates: pd.Series) -> float:
        """
        Calculate the compound annual growth rate from a series

        Args:
            series (pd.Series): Series of index levels
            dates (pd.Series): Dates corresponding to the series

        Returns:
            float: Compound annual growth rate
        """
        start_value = series[0]
        end_value = series.iloc[-1]
        start_date = dates[0]
        end_date = dates.iloc[-1]
        n_years = (end_date - start_date).days / 365.25
        return np.power(end_value / start_value, 1 / n_years) - 1

    def ratio(self, portfolio_return: float, risk_free: float, std: float) -> float:
        """
        Function to calculate sharpe, sortino / other similar ratios

        Args:
            portfolio_return (float): portfolio return
            risk_free (float): risk free
            std (float): standard deviation

        Returns:
            float: corresponding ratio
        """
        if std == 0:
            result = None
        else:
            result = (portfolio_return - risk_free) / std
        return result

    def drawdown(self, portfolio: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate drawdowns of a given period

        Args:
            portfolio (pd.DataFrame): DataFrame containing portfolio index

        Returns:
            pd.DataFrame: Portfolio drawdown
        """
        rolling_max = portfolio["portfolio"].cummax()
        portfolio["drawdown"] = portfolio["portfolio"] / rolling_max - 1.0
        return portfolio[["date", "drawdown"]]

    def market_correlation(self, portfolio: np.array, market: np.array) -> float:
        """
        Calculate correlation between portfolio and market

        Args:
            portfolio (np.array): portfolio returns
            market (np.array): market returns

        Returns:
            float: correlation coefficient
        """
        return np.corrcoef(portfolio, market)[0, 1]

    def regress_market(self, data: pd.DataFrame) -> Tuple:
        """
        Calculate alpha and beta for portfolio, using linear regression against benchmark

        Args:
            data (pd.DataFrame): DataFrame containing portfolio and benchmark returns

        Returns:
            Tuple: Tuple containing: alpha, beta and r squared
        """
        model = smf.ols(formula="portfolio_returns ~ market_returns", data=data)
        results = model.fit()
        return (
            results.params["Intercept"],
            results.params["market_returns"],
            results.rsquared,
        )

    def metrics(self, portfolio: pd.DataFrame) -> Dict:
        """
        Calculate metrics for a portfolio

        Args:
            portfolio (pd.DataFrame): DataFrame containing portfolio index over time

        Returns:
            Dict: Massive set of metrics
        """
        # Needs to be dynamically loaded eventually
        risk_free = 0.01
        portfolio_m = portfolio.loc[
            (
                (portfolio["date"].dt.is_month_end)
                | (portfolio["date"] == max(portfolio["date"]))
            )
        ].reset_index(drop=True)
        portfolio_y = portfolio.loc[
            (
                (portfolio["date"].dt.is_year_end)
                | (portfolio["date"] == max(portfolio["date"]))
            )
        ].reset_index(drop=True)
        portfolio_m["portfolio_returns"] = self.returns(portfolio_m["portfolio"])
        portfolio_m["market_returns"] = self.returns(portfolio_m["market"])
        portfolio_m = portfolio_m.dropna().reset_index(drop=True)
        portfolio_y["portfolio_returns"] = self.returns(portfolio_y["portfolio"])
        portfolio_y["market_returns"] = self.returns(portfolio_y["market"])
        portfolio_y = portfolio_y.dropna().reset_index(drop=True)
        arithmetic_mean_m = portfolio_m["portfolio_returns"].mean()
        geometric_mean_m = self.geometric_mean(portfolio_m["portfolio_returns"].values)
        arithmetic_mean_y = self.annualise_returns(arithmetic_mean_m)
        geometric_mean_y = self.annualise_returns(geometric_mean_m)
        cagr = self.cagr(portfolio["portfolio"], portfolio["date"])
        market_cagr = self.cagr(portfolio["market"], portfolio["date"])
        negative_returns = portfolio_m.loc[portfolio_m["portfolio_returns"] < 0]
        monthly_std = self.std(portfolio_m["portfolio_returns"])
        negative_std = self.std(negative_returns["portfolio_returns"])
        daily_drawdowns = self.drawdown(portfolio)
        max_drawdown = daily_drawdowns["drawdown"].values.min() * -1.0
        daily_drawdowns
        market_correlation = self.market_correlation(
            portfolio_m["portfolio_returns"].values,
            portfolio_m["market_returns"].values,
        )
        alpha, beta, r_squared = self.regress_market(portfolio_m)
        sharpe_ratio = self.ratio(
            portfolio_return=cagr, risk_free=risk_free, std=monthly_std
        )
        sortino_ratio = self.ratio(
            portfolio_return=cagr, risk_free=risk_free, std=negative_std
        )
        treynor_ratio = self.ratio(portfolio_return=cagr, risk_free=risk_free, std=beta)
        calmar_ratio = cagr / max_drawdown
        active_return = cagr - market_cagr
        tracking_error = self.std(
            portfolio_m["portfolio_returns"] - portfolio_m["market_returns"]
        )
        information_ratio = active_return / tracking_error
        positive_market_periods = portfolio_m.loc[portfolio_m["market_returns"] > 0]
        negative_market_periods = portfolio_m.loc[portfolio_m["market_returns"] < 0]
        upside_capture_ratio = self.geometric_mean(
            positive_market_periods["portfolio_returns"]
        ) / self.geometric_mean(positive_market_periods["market_returns"])
        downside_capture_ratio = self.geometric_mean(
            negative_market_periods["portfolio_returns"]
        ) / self.geometric_mean(negative_market_periods["market_returns"])
        capture_ratio = upside_capture_ratio / downside_capture_ratio
        portfolio_m["date"] = portfolio_m["date"].dt.strftime("%Y-%m-%d")
        portfolio_y["date"] = portfolio_y["date"].dt.strftime("%Y-%m-%d")
        daily_drawdowns["date"] = daily_drawdowns["date"].dt.strftime("%Y-%m-%d")
        result = {
            "metrics": {
                "arithmetic_mean_m": arithmetic_mean_m,
                "arithmetic_mean_y": arithmetic_mean_y,
                "geometric_mean_m": geometric_mean_m,
                "geometric_mean_y": geometric_mean_y,
                "std_m": monthly_std,
                "std_downside_m": negative_std,
                "market_correlation": market_correlation,
                "alpha": alpha,
                "beta": beta,
                "r_squared": r_squared,
                "cagr": cagr,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "treynor_ratio": treynor_ratio,
                "calmar_ratio": calmar_ratio,
                "max_drawdown": max_drawdown,
                "active_return": active_return,
                "tracking_error": tracking_error,
                "information_ratio": information_ratio,
                "upside_capture_ratio": upside_capture_ratio,
                "downside_capture_ratio": downside_capture_ratio,
                "capture_ratio": capture_ratio,
            },
            "annual": {
                "return": json.loads(portfolio_y.to_json(orient="records")),
            },
            "monthly": {
                "return": json.loads(portfolio_m.to_json(orient="records")),
            },
            "daily": {
                "drawdown": json.loads(daily_drawdowns.to_json(orient="records"))
            },
        }
        return result
