from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.database import get_table

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        users = get_table('users')
        result = users.select('*').eq('email', form_data.username).execute()
        
        if not result.data:
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        user = result.data[0]
        
        import bcrypt
        if not bcrypt.checkpw(form_data.password.encode(), user['password_hash'].encode()):
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        import jwt
        import os
        from datetime import datetime, timedelta
        
        token = jwt.encode(
            {"user_id": user['id'], "email": user['email'], "exp": datetime.utcnow() + timedelta(hours=24)},
            os.getenv("JWT_SECRET_KEY"),
            algorithm="HS256"
        )
        
        return {"access_token": token, "token_type": "bearer"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Credenziali non valide")

@router.post("/login")
async def login_json(email: str, password: str):
    try:
        users = get_table('users')
        result = users.select('*').eq('email', email).execute()
        
        if not result.data:
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        user = result.data[0]
        
        import bcrypt
        if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            raise HTTPException(status_code=401, detail="Credenziali non valide")
        
        import jwt
        import os
        from datetime import datetime, timedelta
        
        token = jwt.encode(
            {"user_id": user['id'], "email": user['email'], "exp": datetime.utcnow() + timedelta(hours=24)},
            os.getenv("JWT_SECRET_KEY"),
            algorithm="HS256"
        )
        
        return {"access_token": token, "token_type": "bearer"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Credenziali non valide")
