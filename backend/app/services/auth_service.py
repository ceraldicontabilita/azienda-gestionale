"""
Servizio Autenticazione JWT
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import bcrypt
import logging

from app.database import get_table

logger = logging.getLogger(__name__)

# Configurazione JWT
SECRET_KEY = "your-secret-key-change-in-production-use-env"
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
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
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
        ragione_sociale: str,
        partita_iva: str
    ) -> Dict:
        """Registra nuovo utente"""
        try:
            utenti_table = get_table('utenti')
            
            # Verifica email già esistente
            existing = utenti_table.select('*').eq('email', email).execute()
            if existing.data:
                raise ValueError("Email già registrata")
            
            # Hash password
            password_hash = AuthService.hash_password(password)
            
            # Crea utente
            result = utenti_table.insert({
                'email': email,
                'password_hash': password_hash,
                'ragione_sociale': ragione_sociale,
                'partita_iva': partita_iva,
                'attivo': True,
                'created_at': datetime.now().isoformat()
            }).execute()
            
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
                    "ragione_sociale": user['ragione_sociale']
                }
            }
            
        except Exception as e:
            logger.error(f"Errore register_user: {str(e)}")
            raise
    
    @staticmethod
    async def login_user(email: str, password: str) -> Dict:
        """Login utente"""
        try:
            utenti_table = get_table('utenti')
            
            # Trova utente
            result = utenti_table.select('*').eq('email', email).execute()
            
            if not result.data:
                raise ValueError("Credenziali non valide")
            
            user = result.data[0]
            
            # Verifica password
            if not AuthService.verify_password(password, user['password_hash']):
                raise ValueError("Credenziali non valide")
            
            # Verifica utente attivo
            if not user.get('attivo', True):
                raise ValueError("Utente disattivato")
            
            # Crea token
            token = AuthService.create_access_token({
                "user_id": user['id'],
                "email": user['email']
            })
            
            return {
                "success": True,
                "message": "Login effettuato",
                "token": token,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "ragione_sociale": user['ragione_sociale'],
                    "partita_iva": user['partita_iva']
                }
            }
            
        except Exception as e:
            logger.error(f"Errore login_user: {str(e)}")
            raise
    
    @staticmethod
    async def get_current_user(token: str) -> Optional[Dict]:
        """Ottieni utente corrente da token"""
        try:
            payload = AuthService.verify_token(token)
            if not payload:
                return None
            
            utenti_table = get_table('utenti')
            result = utenti_table.select('*').eq('id', payload['user_id']).execute()
            
            if not result.data:
                return None
            
            user = result.data[0]
            return {
                "id": user['id'],
                "email": user['email'],
                "ragione_sociale": user['ragione_sociale'],
                "partita_iva": user['partita_iva']
            }
            
        except Exception as e:
            logger.error(f"Errore get_current_user: {str(e)}")
            return None
