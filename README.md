# Aurora
Portfolio Analysis API built using FastAPI and hosted on GCP

<p align="center">
<a herf="https://github.com/yeungadrian/PortfolioAnalysis/actions/workflows/python-app.yml"> 
 <img src="https://github.com/yeungadrian/Aurora/actions/workflows/python-app.yml/badge.svg"/> 
 </a>
<a herf="https://github.com/yeungadrian/Aurora/actions/workflows/appengine.yml"> 
 <img src="https://github.com/yeungadrian/Aurora/actions/workflows/appengine.yml/badge.svg"/> 
 </a>
<a href="https://codecov.io/gh/yeungadrian/Aurora" > 
 <img src="https://codecov.io/gh/yeungadrian/Aurora/branch/main/graph/badge.svg?token=MBBQ5ZQSBX"/> 
 </a>
</p>


## Financial Analysis:
- Portfolio Backtesting
    - Backtest different asset allocations and compare historical performance
- Factor Analysis
    - Run regression analysis using French-Fama / other factor models
- Portfolio Optimisation
    - Generate efficient frontiers to explore risk return trade offs




## Get Started:
Get started locally by creating a virtual environment via conda or venv and running:
```
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
or using docker
```
docker build -t aurora .
docker run -d --name aurora -p 8000:8000 aurora
```

And view docs at: localhost:8000/docs. Becareful of using both methods and conflicts over the same port.

![](images\apidocs.JPG)

## Technical Features:
### Pure python
- Simple to write
- Uses [FastAPI](https://fastapi.tiangolo.com/)
### Automatic Tests
- Test coverage reports using codecov & pytest
### Continous Integration
- Pre-commit
- CI using Github Actions
### Continious Deployment
- CD using Google Cloud Platform (free tier)


