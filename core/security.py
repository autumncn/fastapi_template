import base64
from datetime import datetime,timedelta
from typing import Any, Union, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Header
import time, hashlib

from core.config import settings
from core.error import AccessTokenFail

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # 加密密码

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def check_jwt_token(token: Optional[str] = Header(...)) -> Union[str, Any]:
    """ 解密token """
    try:
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception as e:  # jwt.JWTError, jwt.ExpiredSignatureError, AttributeError
        raise AccessTokenFail(f'token已过期! -- {e}')

async def get_password_hash(password: str) -> str:
    """ 加密明文密码 """
    return pwd_context.hash(password)

async def verify_password(password: str, hashed_password: str) -> bool:
    """ 验证明文密码 与 加密后的密码 是否一致 """
    return pwd_context.verify(password, hashed_password)

async def create_uid():
    m = hashlib.md5(str(time.perf_counter()).encode("utf-8"))
    return str(m.hexdigest())

