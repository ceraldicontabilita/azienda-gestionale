"""
FastAPI Main Application
Sistema Gestionale Aziendale Completo
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
from dotenv import load_dotenv

# Import database
from app.database import db, startup as db_startup, shutdown as db_shutdown

# Load environment
load_dotenv()

# Create app
app = FastAPI(
    title="Sistema Gestionale Aziendale",
    description="API completa per gestione HR, contabilità, magazzino, HACCP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specificare domini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# IMPORT ROUTERS
# ============================================================================

# AUTH ROUTER (IMPORTANTE!)
try:
    from app.routers.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    print("✅ Auth router loaded")
except Exception as e:
    print(f"⚠️ Auth router not loaded: {e}")

try:
    from app.routers.hr_admin import router as hr_admin_router
    app.include_router(hr_admin_router, prefix="/api/hr", tags=["HR Admin"])
    print("✅ HR Admin router loaded")
except Exception as e:
    print(f"⚠️ HR Admin router not loaded: {e}")

try:
    from app.routers.employee_portal import router as employee_portal_router
    app.include_router(employee_portal_router, prefix="/api/portale", tags=["Employee Portal"])
    print("✅ Employee Portal router loaded")
except Exception as e:
    print(f"⚠️ Employee Portal router not loaded: {e}")

try:
    from app.routers.dipendenti import router as dipendenti_router
    app.include_router(dipendenti_router, prefix="/api/dipendenti", tags=["Dipendenti"])
    print("✅ Dipendenti router loaded")
except Exception as e:
    print(f"⚠️ Dipendenti router not loaded: {e}")

try:
    from app.routers.bonifici import router as bonifici_router
    app.include_router(bonifici_router, prefix="/api/bonifici", tags=["Bonifici"])
    print("✅ Bonifici router loaded")
except Exception as e:
    print(f"⚠️ Bonifici router not loaded: {e}")

try:
    from app.routers.controllo_mensile import router as controllo_router
    app.include_router(controllo_router, prefix="/api/controllo-mensile", tags=["Controllo Mensile"])
    print("✅ Controllo Mensile router loaded")
except Exception as e:
    print(f"⚠️ Controllo Mensile router not loaded: {e}")

try:
    from app.routers.comparatore_prezzi import router as comparatore_router
    app.include_router(comparatore_router, prefix="/api/comparatore", tags=["Comparatore Prezzi"])
    print("✅ Comparatore Prezzi router loaded")
except Exception as e:
    print(f"⚠️ Comparatore Prezzi router not loaded: {e}")

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sistema Gestionale Aziendale API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db.pool else "disconnected",
        "services": {
            "hr": "online",
            "contabilità": "online",
            "magazzino": "online",
            "auth": "online"
        }
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Errore: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error"}
    )


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print("🚀 Sistema Gestionale Aziendale - Starting...")
    print("📊 Connecting to database...")
    await db_startup()
    print("✅ Server ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print("👋 Shutting down...")
    await db_shutdown()


# ============================================================================
# DEVELOPMENT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
