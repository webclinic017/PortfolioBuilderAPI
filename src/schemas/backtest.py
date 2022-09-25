from pydantic import BaseModel


class portfolio(BaseModel):
    start_date: str
    end_date: str
    portfolio: list
    strategy: dict

    class Config:
        schema_extra = {
            "example": {
                "start_date": "2018-12-31",
                "end_date": "2020-06-30",
                "portfolio": [
                    {"fund": "ABMD", "amount": 1000},
                    {"fund": "ATVI", "amount": 1000},
                ],
                "strategy": {"rebalance": True, "rebalance_frequency": "Y"},
            }
        }
