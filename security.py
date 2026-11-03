import os, hmac, hashlib, secrets, time, base64
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = os.getenv("APP_SECRET", "development-only-change-this-secret")

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd.verify(password, hashed)

def make_token(username: str) -> str:
    payload = f"{username}|{int(time.time())}|{secrets.token_hex(8)}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload.encode() + b"." + sig).decode()

def read_token(token: str):
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        payload, sig = raw.rsplit(b".", 1)
        expected = hmac.new(SECRET.encode(), payload, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected): return None
        username, issued, nonce = payload.decode().split("|")
        if time.time() - int(issued) > 60 * 60 * 24 * 7: return None
        return username
    except Exception:
        return None
