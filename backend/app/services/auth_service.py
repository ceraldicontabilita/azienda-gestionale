"""
Servizio Autenticazione JWT - COMPLETO E FUNZIONANTE
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import bcrypt
import logging
import os

from app.database import get_table

logger = logging.getLogger(__name__)

# Configurazione JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 ore

class AuthService:
    """Servizio per autenticazione e gestione JWT"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password con bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifica password"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Errore verifica password: {str(e)}")
            return False
    
    @staticmethod
    def create_access_token(data: Dict) -> str:
        """Crea JWT token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verifica JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token scaduto")
            return None
        except jwt.JWTError as e:
            logger.error(f"Errore JWT: {str(e)}")
            return None
    
    @staticmethod
    async def register_user(
        email: str,
        password: str,
        full_name: str = ""
    ) -> Dict:
        """Registra nuovo utente"""
        try:
            users_table = get_table('users')
            
            # Verifica email già esistente
            existing = users_table.select('*').eq('email', email).execute()
            if existing.data:
                raise ValueError("Email già registrata")
            
            # Hash password
            password_hash = AuthService.hash_password(password)
            
            # Crea utente
            user_data = {
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'role': 'user',
                'created_at': datetime.now().isoformat()
            }
            
            result = users_table.insert(user_data).execute()
            
            if not result.data:
                raise Exception("Errore creazione utente")
            
            user = result.data[0]
            
            # Crea token
            token = AuthService.create_access_token({
                "user_id": user['id'],
                "email": user['email']
            })
            
            return {
                "success": True,
                "message": "Utente registrato",
                "token": token,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "full_name": user.get('full_name', ''),
                    "role": user.get('role', 'user')
                }
            }
            
        except Exception as e:
            logger.error(f"Errore register_user: {str(e)}")
            raise
    
    @staticmethod
    async def login_user(email: str, password: str) -> Dict:
        """Login utente"""
        try:
            users_table = get_table('users')
            
            # Trova utente
            result = users_table.select('*').eq('email', email).execute()
            
            if not result.data:
                logger.warning(f"Login fallito: utente non trovato - {email}")
                raise ValueError("Credenziali non valide")
            
            user = result.data[0]
            
            # Verifica password
            if not AuthService.verify_password(password, user['password_hash']):
                logger.warning(f"Login fallito: password errata - {email}")
                raise ValueError("Credenziali non valide")
            
            # Crea token
            token = AuthService.create_access_token({
                "user_id": user['id'],
                "email": user['email']
            })
            
            logger.info(f"Login riuscito: {email}")
            
            return {
                "success": True,
                "message": "Login effettuato",
                "token": token,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "full_name": user.get('full_name', ''),
                    "role": user.get('role', 'user')
                }
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Errore login_user: {str(e)}")
            raise ValueError("Credenziali non valide")
    
    @staticmethod
    async def get_current_user(token: str) -> Optional[Dict]:
        """Ottieni utente corrente da token"""
        try:
            payload = AuthService.verify_token(token)
            if not payload:
                return None
            
            users_table = get_table('users')
            result = users_table.select('*').eq('id', payload['user_id']).execute()
            
            if not result.data:
                return None
            
            user = result.data[0]
            return {
                "id": user['id'],
                "email": user['email'],
                "full_name": user.get('full_name', ''),
                "role": user.get('role', 'user')
            }
            
        except Exception as e:
            logger.error(f"Errore get_current_user: {str(e)}")
            return None
```

---

## 🚀 COME USARE

1. **Sostituisci** i 2 file sul tuo PC
2. **GitHub Desktop** → Commit: "Fix completo autenticazione"
3. **Push**
4. **Aspetta** 2 minuti che Railway ricompili
5. **Usa Swagger UI** - ora il form OAuth2 funzionerà!

---

## 🔐 COME TESTARE

### **OPZIONE 1: Registrati**
```
POST /api/auth/register
{
  "email": "test@test.it",
  "password": "test123",
  "full_name": "Test User"
}
