from fastapi import HTTPException
from sqlalchemy.orm import Session

from db.models.permissions import Permission
from db.schemas.permissions import PermissionModify, PermissionCreate

def get_permission(db: Session, permission_id: int):
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_permission_by_name(permission_name: str, db: Session):
    permission = db.query(Permission).filter(Permission.name == permission_name).first()
    return permission

def get_permissions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Permission).offset(skip).limit(limit).all()

def modify_permission(db: Session, permission: PermissionModify):
    db_permission = get_permission(db, permission.id)
    db_permission.name = permission.name
    db_permission.description = permission.description
    db_permission.user_ids = permission.user_ids
    db_permission.menu_ids = permission.menu_ids
    db_permission.modify_by = permission.modify_by
    db_permission.modify_time = permission.modify_time
    db.commit()
    db.refresh(db_permission)
    return db_permission

    name: str
    description: str
    user_ids: str
    menu_ids: str
    create_by: str
    create_time: str

def create_permission(db: Session, permission: PermissionCreate):
    db_permission = Permission(
        name=permission.name, description=permission.description,  user_ids=permission.user_ids,
        menu_ids=permission.menu_ids, create_by=permission.create_by, create_time=permission.create_time)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def delete_permission_by_id(db: Session, id: int):
    db_permission = get_permission(db, id)
    db.delete(db_permission)
    db.commit()