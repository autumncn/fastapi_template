from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.models.users import User

from core.security import verify_password
from db.crud.users import get_user_by_email


async def authenticate_user(email: str, password: str, db: AsyncSession):
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
