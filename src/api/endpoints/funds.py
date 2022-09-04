from src.modules.data_loader import DataLoader
from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["Tickers"])
def get_funds():
    result = DataLoader().load_available_funds()

    return result
