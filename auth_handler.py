from decouple import config
from passlib.context import CryptContext
from typing import Dict
import jwt
import time

JWT_SECRET = config("SECRET")
JWT_ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def token_response(token: str, expire_time):
    return {
        "access_token": token,
        "expire_time": str(expire_time)
    }


def signJWT(user_id: str) -> Dict[str, str]:
    expire_time = time.time() + ACCESS_TOKEN_EXPIRE_MINUTES
    payload = {
        "user_id": user_id,
        "expires": expire_time
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token, expire_time)


def checkJWT(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True if decoded_token["expires"] >= time.time() else False
    except:
        return False
