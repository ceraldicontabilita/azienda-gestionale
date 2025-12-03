from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import logging
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

# Importa il client Supabase
try:
    from supabase import create_client
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
except Exception as e:
    logger.error(f"Supabase init error: {e}")
    supabase = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la password con bcrypt"""
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception as e:
        logger.error(f"Password verify error: {e}")
        return False


def create_token(user_id: int, email: str) -> str:
    """Crea JWT token"""
    try:
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(
            payload,
            os.getenv("JWT_SECRET_KEY", "your-secret-key"),
            algorithm="HS256"
        )
        return token
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint - OAuth2 form"""
    try:
        logger.info(f"Login attempt: {form_data.username}")
        
        # Connetti a Supabase
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Cerca l'utente
        response = supabase.table('users').select('*').eq('email', form_data.username).execute()
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        user = response.data[0]
        logger.info(f"User found: {user['email']}, password_hash: {user['password_hash'][:20]}...")
        
        # Verifica password
        if not verify_password(form_data.password, user['password_hash']):
            logger.warning(f"Wrong password for: {form_data.username}")
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        # Crea token
        token = create_token(user['id'], user['email'])
        
        logger.info(f"Login successful: {form_data.username}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user.get('full_name', ''),
                "role": user.get('role', 'user')
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Credenziali non valide")


@router.post("/login")
async def login_json(email: str, password: str):
    """Login endpoint - JSON body"""
    try:
        logger.info(f"Login attempt (JSON): {email}")
        
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not available")
        
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"User not found: {email}")
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        user = response.data[0]
        
        if not verify_password(password, user['password_hash']):
            logger.warning(f"Wrong password for: {email}")
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        token = create_token(user['id'], user['email'])
        
        logger.info(f"Login successful: {email}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user.get('full_name', ''),
                "role": user.get('role', 'user')
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Credenziali non valide")
