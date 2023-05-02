from sqlalchemy.orm import Session

from core.security import verify_password
from db.crud.users import get_user_by_email


def authenticate_user(email: str, password: str, db: Session):
    user = get_user_by_email(email=email, db=db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
