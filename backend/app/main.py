from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.v1 import stocks, markets, predictions, scanner, portfolio, copilot, health, registry_api, backtest_api
from backend.app.websocket import market_ws
from backend.app.websocket.event_bus import market_event_bus


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch real-time tick event bus
    market_event_bus.start()
    yield
    # Shutdown: Clean up event bus
    market_event_bus.stop()


app = FastAPI(
    title="ORION-Q QUANTITATIVE MARKET OS",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS setup for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API Routers
app.include_router(stocks.router, prefix=settings.API_V1_STR, tags=["Stocks"])
app.include_router(markets.router, prefix=settings.API_V1_STR, tags=["Markets"])
app.include_router(predictions.router, prefix=settings.API_V1_STR, tags=["Predictions"])
app.include_router(scanner.router, prefix=settings.API_V1_STR, tags=["Scanner"])
app.include_router(portfolio.router, prefix=settings.API_V1_STR, tags=["Portfolio"])
app.include_router(copilot.router, prefix=settings.API_V1_STR, tags=["Copilot"])
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(registry_api.router, prefix=settings.API_V1_STR, tags=["Model Registry"])
app.include_router(backtest_api.router, prefix=settings.API_V1_STR, tags=["Backtester"])

# WebSocket Router
app.include_router(market_ws.router, prefix=settings.API_V1_STR, tags=["WebSocket"])


@app.get("/")
def root():
    return {
        "project": "ORION-Q QUANTITATIVE MARKET OS",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
