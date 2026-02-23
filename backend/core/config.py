from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX:str="/api"
    DEBUG:bool=False

    DATABASE_URL:str

    ALLOWED_ORIGINS:str=""

    OPENAI_API_KEY:str=""

    HF_API_TOKEN: Optional[str] = None
    HF_MODEL: str = "moonshotai/Kimi-K2-Instruct-0905"
    USE_LOCAL_HF: bool = False

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls,v:str)->List[str]:
        return v.split(",") if v else[]
    
    class Config:
        env_file=".env"
        env_file_encoding="utf-8"
        case_sensitive=True

settings = Settings()
