from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(*, subject: str, secret: str, algorithm: str, expires_minutes: int, extra: dict | None = None) -> str:
    now = _now_utc()
    payload = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, secret, algorithm=algorithm)

def create_refresh_token(*, subject: str, secret: str, algorithm: str, expires_days: int) -> str:
    now = _now_utc()
    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=expires_days)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)
