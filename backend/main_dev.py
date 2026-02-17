"""Development FastAPI application for CloudCostGuard"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import development configuration
from core.config_dev import settings

# Import development routers
from api.cost_routes import router as cost_router
from api.recommendations_routes import router as recommendations_router
from api.analytics_routes import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting CloudCostGuard Development Server...")
    print(f"📊 Debug mode: {settings.debug}")
    print(f"🔗 Database: {settings.database_url}")
    print("📝 Mock data enabled")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down CloudCostGuard Development Server...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="CloudCostGuard Development Server - FinOps Platform for Kubernetes and Azure",
    version=settings.version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    cost_router,
    prefix=f"{settings.api_v1_prefix}/costs",
    tags=["Costs"]
)

app.include_router(
    recommendations_router,
    prefix=f"{settings.api_v1_prefix}/recommendations",
    tags=["Recommendations"]
)

app.include_router(
    analytics_router,
    prefix=f"{settings.api_v1_prefix}/analytics",
    tags=["Analytics"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CloudCostGuard Development Server",
        "version": settings.version,
        "docs": f"{settings.api_v1_prefix}/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.version,
        "debug": settings.debug,
        "mock_data": settings.enable_mock_data
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_dev:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
