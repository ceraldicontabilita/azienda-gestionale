"""
Router Autenticazione - COMPLETO E FUNZIONANTE
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import logging

from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# ============================================================================
# MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    """Modello per registrazione"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def password_strong(cls, v):
        if len(v) < 6:
            raise ValueError('Password deve essere almeno 6 caratteri')
        return v


class LoginRequest(BaseModel):
    """Modello per login JSON"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Risposta con token"""
    access_token: str
    token_type: str
    user: Optional[dict] = None


class UserResponse(BaseModel):
    """Modello utente"""
    id: int
    email: str
    full_name: Optional[str] = None
    role: str


# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Dependency per ottenere utente corrente"""
    try:
        user = await AuthService.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Token non valido o scaduto",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Autenticazione fallita",
            headers={"WWW-Authenticate": "Bearer"}
        )


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/register", response_model=dict)
async def register(request: RegisterRequest):
    """
    Registra nuovo utente
    
    Body:
        - email: email utente
        - password: password (minimo 6 caratteri)
        - full_name: nome completo (opzionale)
    """
    try:
        result = await AuthService.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name or request.email.split('@')[0]
        )
        return result
    except ValueError as e:
        logger.warning(f"Register validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore durante registrazione")


@router.post("/login", response_model=TokenResponse)
async def login_json(request: LoginRequest):
    """
    Login con JSON body
    
    Body:
        - email: email utente
        - password: password
    
    Ritorna:
        - access_token: JWT token
        - token_type: "bearer"
        - user: dati utente
    """
    try:
        result = await AuthService.login_user(
            email=request.email,
            password=request.password
        )
        return {
            "access_token": result["token"],
            "token_type": "bearer",
            "user": result["user"]
        }
    except ValueError as e:
        logger.warning(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Credenziali non valide")


@router.post("/token", response_model=TokenResponse)
async def login_oauth(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login OAuth2 (per Swagger UI)
    
    Usa form-urlencoded:
        - username: email utente
        - password: password
    
    Ritorna:
        - access_token: JWT token
        - token_type: "bearer"
    """
    try:
        result = await AuthService.login_user(
            email=form_data.username,  # OAuth2 usa 'username' ma noi usiamo email
            password=form_data.password
        )
        
        # OAuth2 si aspetta questo formato specifico
        return {
            "access_token": result["token"],
            "token_type": "bearer",
            "user": result["user"]
        }
    except ValueError as e:
        logger.warning(f"OAuth2 login failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"OAuth2 login error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me", response_model=dict)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Ottieni dati utente corrente
    
    Richiede: Bearer token
    
    Ritorna:
        - id, email, full_name, role dell'utente
    """
    return {
        "success": True,
        "user": current_user
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout (client deve eliminare il token)
    
    Richiede: Bearer token
    """
    logger.info(f"Logout: {current_user['email']}")
    return {
        "success": True,
        "message": "Logout effettuato. Elimina il token dal client."
    }


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh del token
    
    Richiede: Bearer token valido (anche vicino alla scadenza)
    
    Ritorna:
        - Nuovo access_token
    """
    try:
        new_token = AuthService.create_access_token({
            "user_id": current_user['id'],
            "email": current_user['email']
        })
        return {
            "access_token": new_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        raise HTTPException(status_code=500, detail="Errore durante refresh token")


@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verifica validità del token
    
    Richiede: Bearer token
    
    Ritorna:
        - Token valido se la richiesta ha successo
    """
    return {
        "valid": True,
        "user": current_user
    }
