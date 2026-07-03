from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.config import settings
from db.database import create_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import job, story

create_tables()

app = FastAPI(
    title="Choose Your Own Adventure Game API",
    description="api to generate cool stories",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Choose Your Own Adventure Game API",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}

