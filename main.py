from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database import init_db
from app.scheduler import start_scheduler, stop_scheduler
from app.middleware.rate_limit import limiter
from app.routers import auth, aqi, weather, forecast, plans, locations, suggestions, dashboard

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("🚀 AirScope API starting up…")
    await init_db()
    print("✅ Database initialised")
    start_scheduler()
    yield
    stop_scheduler()
    print("👋 AirScope API shut down")


app = FastAPI(
    title="AirScope API",
    description=(
        "## AirScope — Breathe With Intelligence\n\n"
        "REST API powering the AirScope air quality platform.\n\n"
        "### Features\n"
        "- **Live AQI** from WAQI (World Air Quality Index)\n"
        "- **Weather** from OpenWeatherMap One Call API\n"
        "- **AI Forecast** — Random Forest model predicting AQI 14 days ahead\n"
        "- **Smart Suggestions** — personalised health & activity recommendations\n"
        "- **Plans & Scheduler** — create, share and manage outdoor activity plans\n"
        "- **User Auth** — JWT-based authentication with health profile\n\n"
        "### Authentication\n"
        "Most endpoints work without auth (public AQI/weather data).\n"
        "Authenticated endpoints require `Authorization: Bearer <token>`."
    ),
    version="1.0.0",
    contact={"name": "AirScope", "email": "api@airscope.app"},
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Rate limiting ──────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(aqi.router)
app.include_router(weather.router)
app.include_router(forecast.router)
app.include_router(plans.router)
app.include_router(locations.router)
app.include_router(suggestions.router)
app.include_router(dashboard.router)


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.app_env,
        "demo_mode": settings.waqi_api_key == "demo",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "AirScope API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ── Global error handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=(settings.app_env == "development"),
        log_level="info",
    )
