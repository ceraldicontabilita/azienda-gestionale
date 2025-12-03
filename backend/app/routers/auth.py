from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from supabase import create_client

router = APIRouter(tags=["Authentication"])
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        result = supabase.table('users').select('*').eq('email', form_data.username).execute()
        if not result.data:
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        user = result.data[0]
        if not bcrypt.checkpw(form_data.password.encode(), user['password_hash'].encode()):
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        token = jwt.encode(
            {"user_id": user['id'], "email": user['email'], "exp": datetime.utcnow() + timedelta(hours=24)},
            os.getenv("JWT_SECRET_KEY"),
            algorithm="HS256"
        )
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
