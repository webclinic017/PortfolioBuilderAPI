from fastapi import APIRouter

from src.api.endpoints import backtest, factor, funds, optimisation

api_router = APIRouter()

api_router.include_router(backtest.router, prefix="/backtest")
api_router.include_router(funds.router, prefix="/funds")
api_router.include_router(factor.router, prefix="/factor_analysis")
api_router.include_router(optimisation.router, prefix="/optimisation")
