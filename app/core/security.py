from datetime import datetime, timedelta, timezone
from jose import jwt
import bcrypt

from app.core.config import settings

# bcrypt usa max 72 bytes del password.
def _pw(password: str) -> bytes:
    return password.encode("utf-8")[:72]

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_pw(password), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(_pw(password), password_hash.encode("utf-8"))

def create_access_token(subject: str) -> dict:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": exp}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return {"token": token, "expiresIn": settings.JWT_EXPIRES_MIN * 60}
