import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_fund_response_code():
    response = client.get("/funds")
    assert response.status_code == 200


def test_fund_value():
    response = client.get("/funds")
    assert response.json()[0]["Code"] == "F00000UEXJ"
    assert response.json()[0]["Company"] == "iShares UK Equity Index Fund"

    assert response.json()[2]["Code"] == "F00000OOB2"
    assert response.json()[2]["Company"] == "HSBC European Index Fund"
