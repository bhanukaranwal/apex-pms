from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import time
from typing import Dict, Any

from backend.core.config import settings
from backend.core.database import engine, Base
from backend.api import auth, portfolios, positions, risk, analytics, optimization, orders, compliance, reports, ai_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="Apex Portfolio Management System",
    description="Institutional-grade portfolio management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"}
    )

@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["System"])
async def root() -> Dict[str, str]:
    return {
        "message": "Apex Portfolio Management System API",
        "docs": "/docs",
        "version": "1.0.0"
    }

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(portfolios.router, prefix="/api/portfolios", tags=["Portfolios"])
app.include_router(positions.router, prefix="/api/positions", tags=["Positions"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk Management"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(optimization.router, prefix="/api/optimization", tags=["Optimization"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(ai_models.router, prefix="/api/ai", tags=["AI/ML"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
