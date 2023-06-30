from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.security import get_password_hash
from db.models.menus import Menu
from db.models.users import User
from db.schemas.menus import MenuModify, MenuCreate
from db.schemas.users import UserCreate, UserModify

async def get_menu(db: AsyncSession, menu_id: int):
    return db.query(Menu).filter(Menu.id == menu_id).first()

async def get_menu_by_name(db: AsyncSession, menu_name: str):
    return db.query(Menu).filter(Menu.name == menu_name).first()

async def get_menu_by_title(db: AsyncSession, menu_title: str):
    return db.query(Menu).filter(Menu.title == menu_title).first()

async def get_menu_by_path(db: AsyncSession, menu_path: str):
    menu = db.execute(select(Menu).filter(Menu.path == menu_path)).scalars().first()
    # return db.query(Menu).filter(Menu.path == menu_path).first()
    return menu

async def get_menus(db: AsyncSession, skip: int = 0, limit: int = 100):
    menus = db.execute(select(Menu).order_by(Menu.level.asc()).offset(skip).limit(limit)).scalars().all()
    # return db.query(Menu).order_by(Menu.level.asc()).offset(skip).limit(limit).all()
    return menus

async def get_menus_by_ids(db: AsyncSession, menu_ids=[]):
    # menus = db.query(Menu).filter(Menu.id.in_(menu_ids)).all()
    menus = db.query(Menu).filter(Menu.id.in_(menu_ids)).order_by(Menu.level.asc()).all()
    return menus

async def modify_menu(db: AsyncSession, menu: MenuModify):
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

async def create_menu(db: AsyncSession, menu: MenuCreate):
    db_menu = Menu(**menu.dict())
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu

async def delete_menu_by_id(db: AsyncSession, id: int):
    db_menu = get_menu(db, id)
    db.delete(db_menu)
    db.commit()