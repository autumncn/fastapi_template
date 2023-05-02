from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.security import get_password_hash
from db.models.users import User
from db.schemas.users import UserCreate, UserModify, UpdateUserLogin, UpdateUserRole, UpdateUserLang

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(username: str, db: Session):
    user = db.query(User).filter(User.email == username).first()
    return user

def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def get_users_by_ids(db: Session, user_ids=[]):
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    return users
    # return db.query(User).filter(User.id in tuple(user_ids)).offset(0).limit(100).all()

def modify_user(db: Session, user: UserModify):
    db_user = get_user(db, user.id)
    db_user.email = user.email
    db_user.username = user.username
    db_user.is_active = user.is_active
    db_user.is_superuser = user.is_superuser
    db_user.modify_by = user.modify_by
    db_user.modify_time = user.modify_time
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.user_role_id = user.user_role_id
    db_user.language = user.language
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user: UpdateUserRole):
    db_user = get_user(db, user.id)
    db_user.user_role_id = user.user_role_id
    db_user.modify_by = user.modify_by
    db_user.modify_time = user.modify_time
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_lang(db: Session, user: UpdateUserLang):
    db_user = get_user(db, user.id)
    db_user.language = user.language
    db_user.modify_by = user.modify_by
    db_user.modify_time = user.modify_time
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_login(db: Session, user: UpdateUserLogin):
    db_user = get_user(db, user.id)
    db_user.date_entered = user.date_entered
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user(db: Session, user: UserCreate):
    # fake_hashed_password = user.password + "notreallyhashed"
    # db_user = User(email=user.email, hashed_password=fake_hashed_password)
    new_hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, username=user.username,  hashed_password=new_hashed_password,
        is_active=1, is_superuser=0, create_by=user.create_by, create_time=user.create_time,
        first_name=user.first_name, last_name=user.last_name,
        user_role_id=user.user_role_id, language=user.language)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_superuser(db: Session, user: UserCreate):
    # fake_hashed_password = user.password + "notreallyhashed"
    # db_user = User(email=user.email, hashed_password=fake_hashed_password)
    new_hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, username=user.username,  hashed_password=new_hashed_password,
        is_active=1, is_superuser=1, create_by=user.create_by, create_time=user.create_time,
        first_name=user.first_name, last_name=user.last_name,
        user_role_id=user.user_role_id, language=user.language)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user_by_id(db: Session, id: int):
    db_user = get_user(db, id)
    db.delete(db_user)
    db.commit()