from fastapi import APIRouter
from backend.app.services.portfolio_engine import portfolio_engine, PortfolioSummary

router = APIRouter()


@router.get("/portfolio-intelligence", response_model=PortfolioSummary)
def get_portfolio_intelligence():
    return portfolio_engine.get_portfolio_intelligence()
