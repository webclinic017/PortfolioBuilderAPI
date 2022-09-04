from typing import List, Optional, TypeVar

import numpy as np
import pandas as pd
from pydantic import BaseModel

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")


class Portfolio(BaseModel):
    codes: List[str]
    amounts: List[float]
    start_date: str
    end_date: str
    timeseries: PandasDataFrame
    rebalance: bool
    rebalance_frequency: Optional[str] = None
    frequency_map = Dict = {"y": 12, "q": 3, "m": 1}

    def normalise_index(self, timeseries):
        initial_index = timeseries[self.codes].iloc[0]
        result = timeseries[self.codes].divide(initial_index, axis=1)
        result["date"] = timeseries["date"]
        return result

    def backtest_portfolio(self, initial_amounts, timeseries):
        n_funds = len(self.codes)
        fund_diagonal = np.zeros((n_funds, n_funds))
        np.fill_diagonal(fund_diagonal, initial_amounts)

        result = timeseries[self.codes].dot(fund_diagonal)

        result.columns = self.codes

        result["portfolio"] = result.sum(axis=1)
        result["date"] = timeseries["date"]

        return result

    def backtest_strategy(self):

        if self.rebalance:
            weights = [i / sum(self.amounts) for i in self.amounts]
            rebalance_frequency = self.frequency_map[self.rebalance_frequency.lower()]

            date_range = pd.Series(
                pd.date_range(start=self.start_date, end=self.end_date, freq="D")
            )
            month_end_dates = date_range[date_range.dt.is_month_end].reset_index(
                drop=True
            )
            rebalancing_dates = (
                month_end_dates[month_end_dates.index % rebalance_frequency == 0]
                .reset_index(drop=True)
                .dt.strftime("%Y-%m-%d")
                .values.tolist()
            )

            if self.start_date not in rebalancing_dates:
                rebalancing_dates.insert(0, self.start_date)

            if self.end_date not in rebalancing_dates:
                rebalancing_dates.append(self.end_date)

            current_total = sum(self.amounts)

            portfolio_history = []

            start_period = rebalancing_dates[0]

            for i in range(0, len(rebalancing_dates) - 1):

                end_period = rebalancing_dates[i + 1]

                price_timeseries = self.timeseries.loc[
                    (self.timeseries.date >= start_period)
                    & (self.timeseries.date <= end_period)
                ].reset_index(drop=True)

                price_timeseries = self.normalise_index(price_timeseries)

                amounts = np.multiply(weights, current_total)

                strategy_slice = self.backtest_portfolio(amounts, price_timeseries)

                current_total = strategy_slice.iloc[-1]["portfolio"]
                duplicate = 0 if i == 0 else 1

                portfolio_history.append(strategy_slice.iloc[duplicate:])

                start_period = strategy_slice.iloc[-1]["date"]

            result = pd.concat(portfolio_history)
        else:
            self.timeseries = self.normalise_index(self.timeseries)

            result = self.backtest_portfolio(self.amounts, self.timeseries)

        return result
