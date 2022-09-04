import json

from src import schemas
from src.modules.data_loader import DataLoader
from src.modules.metrics import Metrics
from src.modules.portfolio import Portfolio
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def backtest_portfolio(item: schemas.portfolio):
    portfolio = item.dict()["portfolio"]
    fund_codes = []
    fund_amount = []

    for i in portfolio:
        fund_codes.append(i["fund"])
        fund_amount.append(i["amount"])

    historical_data = DataLoader().load_historical_index(
        fund_codes,
        item.dict()["start_date"],
        item.dict()["end_date"],
    )

    projection = Portfolio(
        codes=fund_codes,
        amounts=fund_amount,
        start_date=item.dict()["start_date"],
        end_date=item.dict()["end_date"],
        timeseries=historical_data,
        rebalance=item.dict()["strategy"]["rebalance"],
        rebalance_frequency=item.dict()["strategy"]["rebalance_frequency"],
    ).backtest_strategy()

    sp500 = DataLoader().load_benchmark(
        item.dict()["start_date"], item.dict()["end_date"]
    )

    projection = projection.merge(sp500[["date", "market"]], how="left", on="date")

    metrics = Metrics().metrics(projection)

    projection["date"] = projection["date"].dt.strftime("%Y-%m-%d")

    result = {}
    result["projection"] = json.loads(projection.to_json(orient="records"))
    result["metrics"] = metrics

    return result
