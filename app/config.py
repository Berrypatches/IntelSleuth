import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    
    # API keys
    IPINFO_API_KEY: str = os.environ.get("IPINFO_API_KEY", "")
    HUNTER_API_KEY: str = os.environ.get("HUNTER_API_KEY", "")
    HIBP_API_KEY: str = os.environ.get("HIBP_API_KEY", "")
    
    # Default webhook
    DEFAULT_WEBHOOK_URL: str = os.environ.get("DEFAULT_WEBHOOK_URL", "")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 60))
    
    # Scraping settings
    USER_AGENT: str = "OSINT Microagent/1.0"
    TIMEOUT: int = 30
    MAX_RESULTS_PER_SOURCE: int = 10
    
    model_config = {
        "env_file": ".env"
    }

settings = Settings()
