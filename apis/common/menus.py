import datetime
import time
from fastapi.params import Form
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Type
from starlette.responses import RedirectResponse, FileResponse
from fastapi import Request
from dependencies import templates
from starlette import status
from libs.fastapi_babel import _

from db.crud.menus import get_menu, create_menu, get_menus, delete_menu_by_id, modify_menu, get_menu_by_name
from db.database import get_db
from db.schemas.menus import MenuCreate, Menu, MenuModify
from logs.logger import logger
from service.menuService import get_menu_list
from utils.JsonUtil import object_to_json
from utils.ResponseUtil import JsonResponse

router = APIRouter()

@router.get("/", response_model=List[Menu])
def read_menu_list(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menus = get_menus(db, skip=skip, limit=limit)
    new_menu = MenuCreate
    return templates.TemplateResponse("view/menus/menus.html", {"request": request, "menu_list": menus, "new_menu": new_menu})

@router.get("/create", response_model=Menu)
def create_menu_get(request: Request, db: Session = Depends(get_db)):
    new_menu = MenuCreate
    return templates.TemplateResponse("view/menus/menu_create.html", {"request": request, "new_menu": new_menu})

@router.post("/create", response_model=Menu)
async def create_menu_post(request: Request,
        menu_name: str = Form(...),
        path: str = Form(...),
        parent_id: Optional[int] = Form(...),
        icon: Optional[str] = Form(...),
        redirect: Optional[str] = Form(...),
        title: str = Form(...),
        hidden: int = Form(...),
        menu_type: str = Form(...),
        component: Optional[str] = Form(...),
        sort: Optional[int] = Form(...),
        level: Optional[int] = Form(...),
        menu_status: int = Form(...),
        db: Session = Depends(get_db)
):
    db_menu = get_menu_by_name(menu_name=menu_name, db=db)
    if db_menu:
        request.session["error"] = _("menu_already_exists")
        return RedirectResponse('/menus/create', status_code=status.HTTP_400_BAD_REQUEST)

    new_menu = MenuCreate(
        name=menu_name,
        path=path,
        parent_id=parent_id,
        icon=icon,
        redirect=redirect,
        title=title,
        hidden=hidden,
        type=menu_type,
        component=component,
        sort=sort,
        level=level,
        status=menu_status
    )

    create_menu(db=db, menu=new_menu)
    request.session["message"] = _("success_saved")

    response = RedirectResponse('/menus', status_code=status.HTTP_302_FOUND)
    return response

@router.get("/{id}/view")
async def read_menu_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    menu = get_menu(db, menu_id=int(id))
    if menu is None:
        request.session["error"] = _("menu_not_found")
        return RedirectResponse('/menus', status_code=status.HTTP_404_NOT_FOUND)

    new_menu = object_to_json(menu)
    return templates.TemplateResponse("view/menus/menu_view.html", {"request": request, "menu": new_menu})

@router.get("/{id}/modify")
async def edit_menu_by_id_get(request: Request, id: str, db: Session = Depends(get_db)):
    menu = get_menu(db, menu_id=int(id))
    if menu is None:
        request.session["error"] = _("menu_not_found")
        return RedirectResponse('/menus', status_code=status.HTTP_404_NOT_FOUND)

    new_menu = object_to_json(menu)
    return templates.TemplateResponse("view/menus/menu_edit.html", {"request": request, "menu": new_menu})

@router.post("/{id}/modify")
async def edit_menu_by_id_post(request: Request,
        menu_id: str = Form(...),
        menu_name: str = Form(...),
        path: str = Form(...),
        parent_id: Optional[int] = Form(...),
        icon: Optional[str] = Form(...),
        redirect: Optional[str] = Form(...),
        title: str = Form(...),
        hidden: int = Form(...),
        menu_type: str = Form(...),
        component: Optional[str] = Form(...),
        sort: Optional[int] = Form(...),
        level: Optional[int] = Form(...),
        menu_status: int = Form(...),
        db: Session = Depends(get_db)):
    menu = get_menu(db, menu_id=int(menu_id))
    if menu is None:
        request.session["error"] = _("menu_not_found")
        return RedirectResponse('/menus', status_code=status.HTTP_404_NOT_FOUND)

    new_menu = MenuModify(
        id=menu_id,
        name=menu_name,
        path=path,
        parent_id=parent_id,
        icon=icon,
        redirect=redirect,
        title=title,
        hidden=hidden,
        type=menu_type,
        component=component,
        sort=sort,
        level=level,
        status=menu_status
    )

    modify_menu(db, new_menu)
    request.session["message"] = _("success_saved")

    return RedirectResponse('/menus', status_code=status.HTTP_302_FOUND)

@router.post("/{id}/delete", response_model=Menu)
async def delete_menu(request: Request, id: str, db: Session = Depends(get_db)
):
    delete_menu_by_id(db, id)
    request.session["message"] = _("success_deleted")
    response = RedirectResponse('/menus', status_code=status.HTTP_302_FOUND)
    return response

@router.get("/menu_list")
def get_sys_menus(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menu_items = get_menu_list(skip=skip, limit=limit, db=db)

    return JsonResponse(code=200, data=menu_items, message="Success")
