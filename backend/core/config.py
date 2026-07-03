import json
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX:str="/api"
    DEBUG:bool=False

    DATABASE_URL:str

    ALLOWED_ORIGINS: str = ""


    HF_API_TOKEN: Optional[str] = None
    HF_MODEL: str = "moonshotai/Kimi-K2-Instruct-0905"
    USE_LOCAL_HF: bool = False

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_allowed_origins(cls, v):
        if isinstance(v, list):
            return ",".join(str(origin) for origin in v)
        if isinstance(v, str):
            value = v.strip()
            if not value:
                return ""
            if value.startswith("["):
                try:
                    parsed = json.loads(value)
                except Exception:
                    return value
                if isinstance(parsed, list):
                    return ",".join(str(origin) for origin in parsed)
            return value
        return ""

    @property
    def allowed_origins(self) -> list[str]:
        value = self.ALLOWED_ORIGINS.strip()
        if not value:
            return [
                "https://myadventure.vercel.app",
                "https://myadventure-hsjf.vercel.app",
                "http://localhost:5173",
            ]
        if value.startswith("["):
            try:
                parsed = json.loads(value)
            except Exception:
                parsed = []
            if isinstance(parsed, list):
                origins = [str(origin).strip() for origin in parsed if str(origin).strip()]
                return [origin[:-1] if origin.endswith("/") else origin for origin in origins]
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        return [origin[:-1] if origin.endswith("/") else origin for origin in origins]
    
    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding="utf-8"
        case_sensitive=True

settings = Settings()
