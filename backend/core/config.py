from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field

class Settings(BaseSettings):
    API_PREFIX:str="/api"
    DEBUG:bool=False

    DATABASE_URL:str

    ALLOWED_ORIGINS: List[str] = Field(default_factory=list)


    HF_API_TOKEN: Optional[str] = None
    HF_MODEL: str = "moonshotai/Kimi-K2-Instruct-0905"
    USE_LOCAL_HF: bool = False

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    class Config:
        env_file=".env"
        env_file_encoding="utf-8"
        case_sensitive=True

settings = Settings()
