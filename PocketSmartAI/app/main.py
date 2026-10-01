from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import init_db
from app.routes.auth import router as auth_router
from app.routes.pages import router as page_router
from app.routes.planners import router as planner_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(page_router)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(planner_router, prefix="/api", tags=["planners"])

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name, "ai_enabled": bool(settings.ai_enabled and settings.gemini_api_key)}

@app.exception_handler(404)
async def not_found(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return JSONResponse(status_code=404, content={"detail": "Page not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
