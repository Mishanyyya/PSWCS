import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    try:
        password_bytes = password.encode('utf-8')[:72]
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False

def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")