from enum import Enum

from pydantic import BaseModel


class Frequency(str, Enum):
    daily = "daily"
    monthly = "monthly"


class factor(BaseModel):
    start_date: str
    end_date: str
    funds: list
    factors: list
    frequency: Frequency

    class Config:
        schema_extra = {
            "example": {
                "start_date": "2017-12-31",
                "end_date": "2019-12-31",
                "funds": ["AAPL"],
                "factors": ["MktRF", "SMB", "HML"],
                "frequency": Frequency.daily,
            }
        }
