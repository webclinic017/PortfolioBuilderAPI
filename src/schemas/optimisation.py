from pydantic import BaseModel


class optimisation(BaseModel):
    start_date: str
    end_date: str
    funds: list
    num_portfolios: int

    class Config:
        schema_extra = {
            "example": {
                "start_date": "2015-12-31",
                "end_date": "2019-12-31",
                "funds": ["AAPL", "AMZN", "AMD"],
                "num_portfolios": 4,
            }
        }
