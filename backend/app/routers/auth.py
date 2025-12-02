"""
Router Autenticazione
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel, EmailStr
import logging

from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    ragione_sociale: str
    partita_iva: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency per ottenere utente corrente"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token mancante")
    
    try:
        token = authorization.replace("Bearer ", "")
        user = await AuthService.get_current_user(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Token non valido")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Autenticazione fallita")

@router.post("/register")
async def register(request: RegisterRequest):
    """
    Registra nuovo utente
    
    Returns:
    - token JWT
    - dati utente
    """
    try:
        result = await AuthService.register_user(
            email=request.email,
            password=request.password,
            ragione_sociale=request.ragione_sociale,
            partita_iva=request.partita_iva
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Errore register: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore durante registrazione")

@router.post("/login")
async def login(request: LoginRequest):
    """
    Login utente
    
    Returns:
    - token JWT
    - dati utente
    """
    try:
        result = await AuthService.login_user(
            email=request.email,
            password=request.password
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Errore login: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore durante login")

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    """
    Ottieni dati utente corrente
    
    Richiede: Header Authorization: Bearer <token>
    """
    return {
        "success": True,
        "user": current_user
    }

@router.post("/logout")
async def logout():
    """
    Logout (client deve eliminare il token)
    """
    return {
        "success": True,
        "message": "Logout effettuato. Elimina il token dal client."
    }
