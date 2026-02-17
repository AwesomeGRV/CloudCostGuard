from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Optional
import structlog

from core.database import get_db
from core.config import settings
from models.schemas import (
    CostOverviewResponse, NamespaceCostResponse, CostTrendResponse,
    OptimizationRecommendation, CostComparison
)
from api.cost_routes import router as cost_router
from api.recommendations_routes import router as recommendations_router
from api.analytics_routes import router as analytics_router

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Open-source FinOps platform for Kubernetes and Azure cost management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cost_router, prefix=settings.api_v1_prefix)
app.include_router(recommendations_router, prefix=settings.api_v1_prefix)
app.include_router(analytics_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "CloudCostGuard API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.app_version
    }


@app.on_event("startup")
async def startup_event():
    """
    Application startup event
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize database tables
    from core.database import engine
    from models.cost_models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    """
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
