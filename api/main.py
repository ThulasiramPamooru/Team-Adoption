"""
FlowGuard API — FastAPI application entry point
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import create_tables
from app.core.auth import verify_token
from app.routers import auth, workflows, reports, integrations, dashboard
from app.services.websocket_manager import manager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic in production)
    await create_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(workflows.router, prefix=PREFIX)
app.include_router(reports.router, prefix=PREFIX)
app.include_router(integrations.router, prefix=PREFIX)
app.include_router(dashboard.router, prefix=PREFIX)


# ── WebSocket endpoint ─────────────────────────
@app.websocket("/ws/workflow/{workflow_id}")
async def workflow_websocket(websocket: WebSocket, workflow_id: str, token: str = ""):
    # Validate JWT token from query param
    try:
        if token:
            verify_token(token)
    except Exception:
        await websocket.close(code=4001)
        return

    await manager.connect(workflow_id, websocket)
    try:
        while True:
            # Keep alive — client sends pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(workflow_id, websocket)


# ── Health check ───────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
    }
