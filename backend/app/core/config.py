import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ORION-Q Market Intelligence Terminal"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Supported Markets
    SUPPORTED_MARKETS: List[str] = ["INDIA", "US", "GLOBAL"]
    DEFAULT_MARKET_MODE: str = "AUTO"  # AUTO | INDIA | US | GLOBAL
    
    # Supported Symbols
    DEFAULT_INDIA_SYMBOLS: List[str] = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", 
        "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LTIM.NS", "TATAMOTORS.NS"
    ]
    DEFAULT_US_SYMBOLS: List[str] = [
        "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD", "SPY", "QQQ"
    ]
    
    # Market Indices
    INDIA_INDICES: List[str] = ["^NSEI", "^BSESN", "^NSEBANK", "^INDIAVIX"]
    US_INDICES: List[str] = ["^GSPC", "^IXIC", "^DJI", "^VIX"]
    
    # Storage & Models
    SAVED_MODELS_DIR: str = "saved_models"
    DATA_STORAGE_DIR: str = "data_store"
    
    # WebSocket Config
    WS_HEARTBEAT_INTERVAL: int = 15  # seconds
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


settings = Settings()
