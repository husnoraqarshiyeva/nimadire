from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import engine, Base
from .routers import (
    auth_router, users_router, crm_router,
    erp_router, wms_router, reports_router
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TrendWear Distribution ERP/CRM/WMS API",
    description="Cloud-based ERP, CRM and Warehouse Management Platform for wholesale garment distribution.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(crm_router)
app.include_router(erp_router)
app.include_router(wms_router)
app.include_router(reports_router)

@app.get("/")
def root():
    return {
        "message": "TrendWear Distribution ERP Platform API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}