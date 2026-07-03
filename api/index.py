from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Choose Your Own Adventure Game API"}

# 导入后端的路由
try:
    from pathlib import Path
    import sys
    ROOT_DIR = Path(__file__).resolve().parent.parent
    BACKEND_DIR = ROOT_DIR / "backend"
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))
    
    from routers import story, job
    app.include_router(story.router, prefix="/api")
    app.include_router(job.router, prefix="/api")
except Exception as e:
    print(f"Warning: Could not import backend routers: {e}")

