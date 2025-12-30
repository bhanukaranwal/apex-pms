from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    DATABASE_URL: str
    REDIS_URL: str
    
    SECRET_KEY: str
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501"
    ]
    
    POLYGON_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    
    IBKR_HOST: str = "127.0.0.1"
    IBKR_PORT: int = 7497
    IBKR_CLIENT_ID: int = 1
    
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_API_SECRET: Optional[str] = None
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    REDIS_MAX_CONNECTIONS: int = 50
    
    MAX_POSITIONS_PER_PORTFOLIO: int = 10000
    DEFAULT_CURRENCY: str = "USD"
    
    VAR_CONFIDENCE_LEVELS: List[float] = [0.90, 0.95, 0.99]
    MONTE_CARLO_SIMULATIONS: int = 10000
    
    ML_MODEL_PATH: str = "backend/models/saved"
    
    @property
    def jwt_secret(self) -> str:
        return self.JWT_SECRET_KEY or self.SECRET_KEY

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
