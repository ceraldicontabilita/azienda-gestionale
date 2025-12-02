"""
FastAPI Main Application
Sistema Gestionale Aziendale Completo
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Import database
from app.database import db, get_db, startup as db_startup, shutdown as db_shutdown

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
# DATABASE CONNECTION
# ============================================================================

# Usa il modulo database.py per connessione Supabase/AsyncPG
# get_db() è ora importato da app.database


# ============================================================================
# AUTHENTICATION (Placeholder)
# ============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class User:
    """User model placeholder"""
    def __init__(self, id: int, username: str, role: str):
        self.id = id
        self.username = username
        self.role = role


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user"""
    # TODO: Implementare validazione JWT
    # Per ora ritorna utente mock
    return User(id=1, username="admin", role="admin")


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


async def get_current_employee_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current employee user"""
    # TODO: Implementare
    return User(id=1, username="employee", role="employee")


async def get_employee_by_user_id(user_id: int, db):
    """Get employee by user_id"""
    # TODO: Implementare query
    class MockEmployee:
        id = 1
        nome = "Mario"
        cognome = "Rossi"
    return MockEmployee()


# ============================================================================
# IMPORT ROUTERS
# ============================================================================

try:
    from app.routers.hr_admin import router as hr_admin_router
    app.include_router(hr_admin_router)
    print("✅ HR Admin router loaded")
except Exception as e:
    print(f"⚠️  HR Admin router not loaded: {e}")

try:
    from app.routers.employee_portal import router as employee_portal_router
    app.include_router(employee_portal_router)
    print("✅ Employee Portal router loaded")
except Exception as e:
    print(f"⚠️  Employee Portal router not loaded: {e}")

try:
    from app.routers.dipendenti import router as dipendenti_router
    app.include_router(dipendenti_router)
    print("✅ Dipendenti router loaded")
except Exception as e:
    print(f"⚠️  Dipendenti router not loaded: {e}")

try:
    from app.routers.bonifici import router as bonifici_router
    app.include_router(bonifici_router)
    print("✅ Bonifici router loaded")
except Exception as e:
    print(f"⚠️  Bonifici router not loaded: {e}")

try:
    from app.routers.controllo_mensile import router as controllo_router
    app.include_router(controllo_router)
    print("✅ Controllo Mensile router loaded")
except Exception as e:
    print(f"⚠️  Controllo Mensile router not loaded: {e}")

try:
    from app.routers.comparatore_prezzi import router as comparatore_router
    app.include_router(comparatore_router)
    print("✅ Comparatore Prezzi router loaded")
except Exception as e:
    print(f"⚠️  Comparatore Prezzi router not loaded: {e}")


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
        "database": "connected",  # TODO: Check real DB connection
        "services": {
            "hr": "online",
            "contabilità": "online",
            "magazzino": "online"
        }
    }


@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint
    
    TODO: Implementare autenticazione reale con JWT
    """
    # Mock implementation
    if form_data.username == "admin" and form_data.password == "admin123":
        return {
            "access_token": "mock_token_admin_123",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "admin",
                "role": "admin"
            }
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
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
