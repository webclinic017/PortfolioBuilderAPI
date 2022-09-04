import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_fund_response_code():
    response = client.get("/funds")
    assert response.status_code == 200


def test_fund_value():
    response = client.get("/funds")
    assert response.json()[0]["Code"] == "ABMD"
    assert response.json()[0]["Company"] == "ABIOMED Inc"


def test_fund_value():
    response = client.get("/funds")
    assert response.json()[2]["Code"] == "AMD"
    assert response.json()[2]["Company"] == "Advanced Micro Devices Inc"
