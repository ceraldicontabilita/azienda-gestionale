"""
Router Autenticazione - COMPLETO E FUNZIONANTE
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from pydantic import BaseModel, EmailStr
import logging

from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency per ottenere utente corrente"""
    try:
        user = await AuthService.get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Token non valido")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Autenticazione fallita")

@router.post("/register")
async def register(request: RegisterRequest):
    """Registra nuovo utente"""
    try:
        result = await AuthService.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Errore register: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore durante registrazione")

@router.post("/login")
async def login_json(request: LoginRequest):
    """Login con JSON body"""
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

@router.post("/token")
async def login_oauth(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login OAuth2 (per Swagger UI)"""
    try:
        result = await AuthService.login_user(
            email=form_data.username,  # OAuth2 usa 'username' ma noi usiamo email
            password=form_data.password
        )
        
        # OAuth2 si aspetta questo formato specifico
        return {
            "access_token": result["token"],
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    except Exception as e:
        logger.error(f"Errore login OAuth2: {str(e)}")
        raise HTTPException(status_code=401, detail="Credenziali non valide")

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    """Ottieni dati utente corrente"""
    return {
        "success": True,
        "user": current_user
    }

@router.post("/logout")
async def logout():
    """Logout (client deve eliminare il token)"""
    return {
        "success": True,
        "message": "Logout effettuato. Elimina il token dal client."
    }
