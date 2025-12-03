"""
Router Autenticazione - FUNZIONANTE SENZA CICLI
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import logging
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

# Supabase - importa QUI direttamente
from supabase import create_client

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
    logger.info("✅ Supabase client initialized in auth")
else:
    supabase = None
    logger.error("❌ Supabase not configured in auth")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login - OAuth2 form"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database error")
        
        email = form_data.username
        password = form_data.password
        
        logger.info(f"Login: {email}")
        
        # Cerca utente
        result = supabase.table('users').select('*').eq('email', email).execute()
        
        if not result.data:
            logger.warning(f"User not found: {email}")
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        user = result.data[0]
        logger.info(f"User found: {user['email']}")
        
        # Verifica password
        if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            logger.warning(f"Wrong password: {email}")
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        # Crea token
        token_data = {
            "user_id": user['id'],
            "email": user['email'],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(
            token_data,
            os.getenv("JWT_SECRET_KEY", "secret"),
            algorithm="HS256"
        )
        
        logger.info(f"✅ Login success: {email}")
        
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(status_code=401, detail="Credenziali non valide")
