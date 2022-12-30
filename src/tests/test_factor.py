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
            "funds": ["F00000UEXJ"],
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
            "funds": ["F00000UEXJ"],
            "factors": ["MktRF", "SMB", "HML"],
            "frequency": "monthly",
        },
    )
    assert response.json()[0]["fund_code"] == "F00000UEXJ"
    assert response.json()[0]["num_observations"] == 12
    assert response.json()[0]["rsquared"] == pytest.approx(0.4168539352208934)
    assert response.json()[0]["fvalue"] == pytest.approx(1.9062299500271107)
    assert response.json()[0]["coefficient"]["Intercept"] == pytest.approx(
        -0.0016291295180895075
    )
    assert response.json()[0]["coefficient"]["MktRF"] == pytest.approx(
        0.369107130361537
    )
    assert response.json()[0]["coefficient"]["SMB"] == pytest.approx(
        0.4497440405163511
    )
    assert response.json()[0]["coefficient"]["HML"] == pytest.approx(
        0.4028992514591269
    )


def test_rolling_regression():
    response = client.post(
        "/factor_analysis/rolling/",
        json={
            "start_date": "2017-12-31",
            "end_date": "2019-12-31",
            "funds": ["F00000UEXJ"],
            "factors": ["MktRF", "SMB", "HML"],
            "frequency": "monthly",
        },
    )
    assert response.json()[0]["fund_code"] == "F00000UEXJ"
    assert response.json()[0]["params"]["Intercept"][
        "2019-12-31"
    ] == pytest.approx(0.0010084235)
    assert response.json()[0]["params"]["MktRF"][
        "2019-12-31"
    ] == pytest.approx(0.6055344585)
    assert response.json()[0]["params"]["SMB"]["2019-12-31"] == pytest.approx(
        -0.2810892952
    )
    assert response.json()[0]["params"]["HML"]["2019-12-31"] == pytest.approx(
        0.2496138221
    )
