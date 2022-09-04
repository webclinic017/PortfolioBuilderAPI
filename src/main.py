from fastapi import FastAPI
from src.api.api import api_router

tags_metadata = [
    {
        "name": "Tickers",
        "description": "Funds / Stocks supported by aurora",
    },
    {
        "name": "Backtest Portfolio",
        "description": "Backtest asset allocations",
    },
    {
        "name": "Portfolio Optimisation",
        "description": "Mean-variance portfolio optimisation",
    },
    {
        "name": "Factor Analysis",
        "description": "Run regression analysis using factor models",
    }
]

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(api_router)
