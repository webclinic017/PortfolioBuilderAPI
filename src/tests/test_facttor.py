import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_regression_response_code():
    response = client.post(
        "/factor_analysis/",
        json={
            "start_date": "2017-12-31",
            "end_date": "2018-12-31",
            "funds": ["AAPL"],
            "factors": ["MktRF", "SMB", "HML"],
            "frequency": "monthly",
        },
    )
    assert response.status_code == 200


def test_apple_regression_12month():
    response = client.post(
        "/factor_analysis/",
        json={
            "start_date": "2017-12-31",
            "end_date": "2018-12-31",
            "funds": ["AAPL"],
            "factors": ["MktRF", "SMB", "HML"],
            "frequency": "monthly",
        },
    )
    assert response.json()[0]["fund_code"] == "AAPL"
    assert response.json()[0]["num_observations"] == 12
    assert response.json()[0]["rsquared"] == 0.3522879912622011
    assert response.json()[0]["fvalue"] == 1.450389417970732
    assert response.json()[0]["coefficient"]["Intercept"] == -0.01643662726827
    assert response.json()[0]["coefficient"]["MktRF"] == 0.38844009528774637
    assert response.json()[0]["coefficient"]["SMB"] == 0.6470689813012082
    assert response.json()[0]["coefficient"]["HML"] == -2.0743626259033987
