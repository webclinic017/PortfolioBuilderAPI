from typing import Any

from fastapi import APIRouter

from src.modules.data_loader import DataLoader

router = APIRouter()


@router.get("/", tags=["Tickers"])
def get_funds() -> Any:
    """
    Load available tickers

    Returns:
        Any: JSON like object with avaliable tickers
    """
    result = DataLoader().load_available_funds()
    return result
