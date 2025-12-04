"""
Router Autenticazione - FUNZIONANTE
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from supabase import create_client

router = APIRouter(tags=["Authentication"])

# Inizializza Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not configured")
        
        # Cerca utente
        result = supabase.table('users').select('*').eq('email', form_data.username).execute()
        
        if not result.data:
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        user = result.data[0]
        
        # Verifica password
        if not bcrypt.checkpw(form_data.password.encode(), user['password_hash'].encode()):
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        # Crea JWT token
        token = jwt.encode(
            {
                "user_id": user['id'],
                "email": user['email'],
                "exp": datetime.utcnow() + timedelta(hours=24)
            },
            os.getenv("JWT_SECRET_KEY", "your-secret-key"),
            algorithm="HS256"
        )
        
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
        raise HTTPException(status_code=401, detail="Credenziali non valide")


@router.post("/login")
async def login_json(email: str, password: str):
    """Login con JSON"""
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not configured")
        
        result = supabase.table('users').select('*').eq('email', email).execute()
        
        if not result.data:
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        user = result.data[0]
        
        if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        token = jwt.encode(
            {
                "user_id": user['id'],
                "email": user['email'],
                "exp": datetime.utcnow() + timedelta(hours=24)
            },
            os.getenv("JWT_SECRET_KEY", "your-secret-key"),
            algorithm="HS256"
        )
        
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
        raise HTTPException(status_code=401, detail="Credenziali non valide")
