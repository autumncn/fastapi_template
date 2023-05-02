from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.security import get_password_hash
from db.models.menus import Menu
from db.models.users import User
from db.schemas.menus import MenuModify, MenuCreate
from db.schemas.users import UserCreate, UserModify

def get_menu(db: Session, menu_id: int):
    return db.query(Menu).filter(Menu.id == menu_id).first()

def get_menu_by_name(db: Session, menu_name: str):
    return db.query(Menu).filter(Menu.name == menu_name).first()

def get_menu_by_title(db: Session, menu_title: str):
    return db.query(Menu).filter(Menu.title == menu_title).first()

def get_menu_by_path(db: Session, menu_path: str):
    return db.query(Menu).filter(Menu.path == menu_path).first()

def get_menus(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Menu).order_by(Menu.level.asc()).offset(skip).limit(limit).all()

def get_menus_by_ids(db: Session, menu_ids=[]):
    # menus = db.query(Menu).filter(Menu.id.in_(menu_ids)).all()
    menus = db.query(Menu).filter(Menu.id.in_(menu_ids)).order_by(Menu.level.asc()).all()
    return menus

def modify_menu(db: Session, menu: MenuModify):
    db_menu = get_menu(db, menu.id)
    db_menu.name = menu.name
    db_menu.path = menu.path
    db_menu.parent_id = menu.parent_id
    db_menu.icon = menu.icon
    db_menu.redirect = menu.redirect
    db_menu.title = menu.title
    db_menu.hidden = menu.hidden
    db_menu.type = menu.type
    db_menu.component = menu.component
    db_menu.sort = menu.sort
    db_menu.level = menu.level
    db_menu.status = menu.status

    db.commit()
    db.refresh(db_menu)
    return db_menu

def create_menu(db: Session, menu: MenuCreate):
    db_menu = Menu(**menu.dict())
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu

def delete_menu_by_id(db: Session, id: int):
    db_menu = get_menu(db, id)
    db.delete(db_menu)
    db.commit()