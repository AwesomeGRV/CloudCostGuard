"""Development configuration for CloudCostGuard"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application settings
    app_name: str = "CloudCostGuard"
    debug: bool = True
    version: str = "1.0.0"
    
    # Database settings (SQLite for development)
    database_url: str = "sqlite+aiosqlite:///./cloudcostguard_dev.db"
    
    # Redis settings (disabled for development)
    redis_url: Optional[str] = None
    
    # Azure settings (mock for development)
    azure_subscription_id: str = "dev-subscription-id"
    azure_client_id: str = "dev-client-id"
    azure_client_secret: str = "dev-client-secret"
    azure_tenant_id: str = "dev-tenant-id"
    
    # Prometheus settings (mock for development)
    prometheus_url: str = "http://localhost:9090"
    
    # Security settings
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # CORS settings
    backend_cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Development mode settings
    enable_mock_data: bool = True
    mock_data_interval: int = 300  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a global settings instance
settings = Settings()
