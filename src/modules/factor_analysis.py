import json
from typing import Dict, List

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from pydantic import BaseModel
from statsmodels.regression.linear_model import RegressionResults
from statsmodels.regression.rolling import RollingOLS
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson


class FactorAnalysis(BaseModel):
    fund_codes: List[str]
    start_date: str
    end_date: str
    factors: List[str]
    fund_returns: pd.DataFrame
    ff_factors: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True

    def get_summary_results(
        self, results: RegressionResults, fund_code: str, exog_het: pd.DataFrame
    ) -> Dict:
        """
        Take the result of an statsmodel results table and transforms it into a dataframe
        https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.html

        Durbin watson test for autocorrelation
        Breusch Pagan test for heteroscedasticity

        Args:
            results (RegressionResults): statsmodel regression results
            fund_code (str): ticker that was regressed
            exog_het (pd.DataFrame): datafra

        Returns:
            Dict: Summary regression results
        """
        pvals = results.pvalues
        coefficient = results.params
        conf_lower = results.conf_int()[0]
        conf_higher = results.conf_int()[1]
        standard_errors = results.bse
        residuals = results.resid
        num_obs = results.nobs
        rsquared = results.rsquared
        rsquared_adj = results.rsquared_adj
        fvalue = results.fvalue
        # 0 - positive autocorrelation, 2 - no autocorrelation, 4 - negative autocorrelation
        dw_test = durbin_watson(residuals)
        bp_test = het_breuschpagan(residuals, exog_het)
        output_result = {
            "fund_code": fund_code,
            "num_observations": num_obs,
            "rsquared": rsquared,
            "rsquared_adj": rsquared_adj,
            "fvalue": fvalue,
            "coefficient": coefficient,
            "standard_errors": standard_errors,
            "pvalues": pvals,
            "conf_lower": conf_lower,
            "conf_higher": conf_higher,
            "durbin_watson": dw_test,
            "breusch_pagan": {"lm": bp_test[0], "lm_pvalue": bp_test[1]},
            "residuals": residuals,
        }
        return output_result

    def generate_features(self, fund_code: str) -> pd.DataFrame:
        """
        Generate timeseries dataframe containing ticker returns and factors

        Args:
            fund_code (str): Ticker to get data for

        Returns:
            pd.DataFrame: _description_
        """
        fund_returns = self.fund_returns.copy()
        ff_factors = self.ff_factors.copy()
        fund_returns["date"] = fund_returns["date"].dt.strftime("%Y-%m-%d")
        ff_factors["date"] = ff_factors["date"].dt.strftime("%Y-%m-%d")
        fund_returns = fund_returns.set_index("date")
        fund_returns.index.name = None
        ff_factors = ff_factors.set_index("date")
        ff_factors.index.name = None
        regression_data = pd.concat([fund_returns, ff_factors], axis=1, join="inner")
        regression_data[fund_code] = regression_data[fund_code] - regression_data["RF"]
        return regression_data

    def calculate_factor_regression(
        self, fund_code: str, regression_factors: List[str]
    ) -> Dict:
        """Factor analysis of ticker against specified factors

        Args:
            fund_code (str): Ticker to regress
            regression_factors (List[str]): regression factors to use

        Returns:
            Dict: regression results
        """
        np.random.seed(1000)
        regression_equation = " + ".join(regression_factors)
        regression_data = self.generate_features(fund_code)
        model = smf.ols(
            formula=f"{fund_code} ~ {regression_equation}", data=regression_data
        )
        results = model.fit()
        exog_het = regression_data[regression_factors + ["RF"]]
        output = self.get_summary_results(results, fund_code, exog_het)
        return output

    def calculate_rolling_regression(
        self, fund_code: str, regression_factors: List[str], frequency: str
    ) -> Dict:
        """
        Rolling regression using 12 month windows to run factor analysis over time

        Args:
            fund_code (str): ticker to regress
            regression_factors (List[str]): regression factors to use
            frequency (str): returns frequency

        Returns:
            Dict: Regression results
        """
        np.random.seed(1000)
        regression_equation = " + ".join(regression_factors)
        regression_data = self.generate_features(fund_code)
        window = 12
        if frequency == "daily":
            window = window * 30
        model = RollingOLS.from_formula(
            formula=f"{fund_code} ~ {regression_equation}",
            data=regression_data,
            window=window,
        )
        results = model.fit()
        output = {
            "fund_code": fund_code,
            "params": json.loads(results.params.to_json()),
            "rsquared": json.loads(results.rsquared.to_json()),
        }
        return output

    def regress_funds(self) -> List[Dict]:
        """
        Run Linear OLS for ticker returns against factors

        Returns:
            List[Dict]: Regresion results as dictionary per ticker
        """
        output = []
        for i in self.fund_codes:
            output.append(self.calculate_factor_regression(i, self.factors))
        return output

    def rolling_regress_funds(self, frequency: str) -> List[Dict]:
        """
        Rolling regression against specified factors for specified tickers

        Args:
            frequency (str): Frequency of factor / ticker returns to regress with

        Returns:
            List[Dict]: Regresion results as dictionary per ticker
        """
        output = []
        for i in self.fund_codes:
            output.append(self.calculate_rolling_regression(i, self.factors, frequency))
        return output
