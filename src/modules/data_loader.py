import json
from datetime import datetime, timedelta
from typing import Any, List

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from pydantic import BaseModel

config = {
    "fund_codes": "src/data/fund_codes.parquet",
    "fund_prices": "src/data/fund_prices.parquet",
    "ff_daily": "src/data/ff_daily.parquet",
    "ff_monthly": "src/data/ff_monthly.parquet",
    "sp500": "src/data/sp500.csv",
}


class DataLoader(BaseModel):
    """
    Portfolio builder method to load parquet / csv files

    """

    class Config:
        arbitrary_types_allowed = True

    def load_available_funds(self) -> Any:
        """
        Load supported list of tickers from parquet file

        Returns:
            pd.DataFrame: ticker and long name

        """
        all_funds = (
            pq.read_table(config["fund_codes"]).to_pandas().to_json(orient="records")
        )
        return json.loads(all_funds)

    def slice_data(
        self, timeseries: pd.DataFrame, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Slice dataframe by specified time period

        Args:
            timeseries (pd.DataFrame): Timeseries containing index / curve
            start_date (str): start date (%Y-%m-%d format)
            end_date (str): end date (%Y-%m-%d format)

        Returns:
            pd.DataFrame

        """
        timeseries["date"] = pd.to_datetime(timeseries["date"])
        timeseries = timeseries[timeseries["date"] >= start_date]
        timeseries = timeseries[timeseries["date"] <= end_date]
        timeseries = timeseries.sort_values("date").reset_index(drop=True)

        return timeseries

    def backfill_ts(
        self,
        timeseries: pd.DataFrame,
        start_date: str,
        end_date: str,
        interpolation: str = None,
    ) -> pd.DataFrame:
        """
        Backfill missing dates using specified interpoliation method and slice based on historical range

        Args:
            timeseries (pd.DataFrame): Timeseries containing index / curve
            start_date (str): start date (%Y-%m-%d format)
            end_date (str): end date (%Y-%m-%d format)
            interpolation (bool=None): Interpolation method (fill or None)

        Returns:
            pd.DataFrame

        """
        data = self.slice_data(timeseries, start_date, end_date)
        if interpolation == "fill":
            idx = pd.date_range(start_date, end_date)
            data = data.set_index("date")
            data.index.name = None
            data.index = pd.DatetimeIndex(data.index)
            data = data.reindex(idx, fill_value=np.nan)
            data = data.interpolate(method="backfill", axis=0)
            data = data.reset_index(drop=False)
            data = data.rename(
                columns={
                    "index": "date",
                }
            )
        return data

    def load_benchmark(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Load benchmark index for specified period (currently only supporting S&P 500)

        Args:
            start_date (str): start date (%Y-%m-%d format)
            end_date (str): end date (%Y-%m-%d format)

        Returns:
            pd.DataFrame
        """
        benchmark = pd.read_csv(config["sp500"], index_col=None)
        benchmark = benchmark.rename(columns={"Date": "date", "Close/Last": "market"})
        benchmark.date = pd.to_datetime(benchmark.date)
        benchmark = benchmark.sort_values(by="date").reset_index(drop=True)
        benchmark = self.backfill_ts(
            benchmark, start_date, end_date, interpolation="fill"
        )
        return benchmark

    def load_historical_index(
        self, fund_codes: List[str], start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Load historical ticker index

        Args:
            fund_codes (List[str]): List of tickers to load
            start_date (str): start date (%Y-%m-%d format)
            end_date (str): end date (%Y-%m-%d format)

        Returns:
            pd.DataFrame:
        """
        columns = ["date"] + fund_codes
        timeseries = pq.read_table(config["fund_prices"], columns=columns).to_pandas()
        data = self.backfill_ts(
            timeseries,
            start_date=start_date,
            end_date=end_date,
            interpolation="fill",
        )
        data.columns = columns
        return data

    def load_historical_returns(
        self, fund_codes: List[str], start_date: str, end_date: str, frequency: str
    ) -> pd.DataFrame:
        """
        Load historical returns for specified tickers and date

        Args:
            fund_codes (List[str]): List of tickers to load
            start_date (str): start date (%Y-%m-%d format)
            end_date (str): end date (%Y-%m-%d format)
            frequency (str): Returns frequency (daily or monthly)

        Returns:
            pd.DataFrame:
        """
        response_columns = ["date"] + fund_codes
        start_date = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=1)
        start_date = datetime.strftime(start_date, "%Y-%m-%d")
        subset_data = pd.DataFrame(
            self.load_historical_index(
                fund_codes=fund_codes, start_date=start_date, end_date=end_date
            )
        )
        if frequency == "monthly":
            subset_data = subset_data[subset_data["date"].dt.is_month_end].reset_index(
                drop=True
            )
        for i in fund_codes:
            subset_data[f"{i}index"] = (subset_data[i] / subset_data[i].shift()) - 1
        subset_data = subset_data.dropna()
        subset_data = subset_data.drop(fund_codes, axis=1)
        subset_data.columns = response_columns

        return subset_data

    def load_ff_factors(
        self,
        regression_factors: List[str],
        start_date: str,
        end_date: str,
        frequency: str = "daily",
    ) -> pd.DataFrame:
        """
        Load French-Fama US factors for specified date range and frequency

        Args:
            regression_factors (List[str]): Factors to load
            start_date (str): start date (%Y-%m-%d format)
            end_date (str): end date (%Y-%m-%d format)
            frequency (str, optional): Frequency of factors

        Returns:
            pd.DataFrame:
        """
        columns = ["date"] + regression_factors + ["RF"]
        factors = pq.read_table(config[f"ff_{frequency}"], columns=columns).to_pandas()
        data = self.backfill_ts(
            factors,
            start_date=start_date,
            end_date=end_date,
            interpolation=None,
        )
        # Kenneth French's data is off by factor of 100
        for k in columns:
            if k != "date":
                data[k] = data[k] / 100
        data.columns = columns
        return data
