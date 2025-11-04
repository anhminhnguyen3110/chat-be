from pydantic_settings import BaseSettings
from enum import Enum
from pathlib import Path
from typing import List
import platform


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    APP_NAME: str = "VPAura"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    LLM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    LLM_API_KEY: str
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "qwen/qwen3-next-80b-a3b-thinking"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    LLM_FALLBACK_MODEL: str = "qwen/qwen3-next-80b-a3b-thinking"
    
    # Environment-aware properties
    @property
    def MAX_LLM_CALL_RETRIES(self) -> int:
        """Environment-specific retry count."""
        return {
            Environment.DEVELOPMENT: 1,
            Environment.TEST: 1,
            Environment.STAGING: 2,
            Environment.PRODUCTION: 3,
        }.get(self.ENVIRONMENT, 2)
    
    @property
    def POSTGRES_POOL_SIZE(self) -> int:
        """Environment-specific pool size."""
        return {
            Environment.DEVELOPMENT: 5,
            Environment.TEST: 3,
            Environment.STAGING: 10,
            Environment.PRODUCTION: 20,
        }.get(self.ENVIRONMENT, 10)
    
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "*"
    
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"
    LOG_DIR: Path = Path("logs")
    
    REDIS_URL: str = "redis://localhost:6379"
    
    ENABLE_GUARDRAIL: bool = True
    
    # Neo4j Configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j"
    NEO4J_DATABASE: str = "neo4j"
    NEO4J_AGENT_MAX_RETRIES: int = 3
    
    # Langfuse Configuration
    LANGFUSE_ENABLED: bool = False
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    # Checkpointer Configuration
    ENABLE_CHECKPOINTER: bool = True
    CHECKPOINT_TABLES: List[str] = ["checkpoints", "checkpoint_writes", "checkpoint_blobs"]
    CHECKPOINT_RETENTION_DAYS: int = 30
    
    @property
    def SHOULD_USE_CHECKPOINTER(self) -> bool:
        """Disable checkpointer in development on Windows to avoid ProactorEventLoop issues."""
        if self.ENVIRONMENT == Environment.DEVELOPMENT:
            # Disable on Windows in development
            if platform.system() == "Windows":
                return False
        return self.ENABLE_CHECKPOINTER
    
    class Config:
        env_file = ".env"


settings = Settings()
