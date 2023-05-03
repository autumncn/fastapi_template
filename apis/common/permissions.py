import datetime
import time
from fastapi.params import Form
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Type
from starlette.responses import RedirectResponse, FileResponse
from fastapi import Request

from db.crud.users import update_user_role
from db.schemas.users import UpdateUserRole
from dependencies import templates
from starlette import status
from libs.fastapi_babel import _

from db.crud.permissions import get_permission, create_permission, get_permissions, modify_permission, get_permission_by_name, delete_permission_by_id
from db.database import get_db
from db.schemas.permissions import PermissionCreate, Permission, PermissionModify
from logs.logger import logger
from service.menuService import menu_list_id_name, get_menu_name_by_id_list
from service.userService import get_user_list, get_user_name_by_id_list
from utils.JsonUtil import object_to_json
from utils.ResponseUtil import JsonResponse

router = APIRouter()

@router.get("/", response_model=List[Permission])
def read_permission_list(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    permissions = get_permissions(db, skip=skip, limit=limit)
    new_permission = PermissionCreate
    return templates.TemplateResponse("view/permissions/permissions.html", {"request": request, "permission_list": permissions, "new_permission": new_permission})

@router.get("/create", response_model=Permission)
def create_permission_get(request: Request, db: Session = Depends(get_db)):
    new_permission = PermissionCreate
    user_list = get_user_list(db=db)
    menu_list = menu_list_id_name(db=db)
    return templates.TemplateResponse("view/permissions/permission_create.html", {"request": request, "new_permission": new_permission, "user_list": user_list, "menu_list": menu_list})

@router.post("/create", response_model=Permission)
async def create_permission_post(request: Request,
        permission_name: str = Form(...),
        permission_description: str = Form(...),
        permission_user_ids: List[str] = Form(alias="multi-select-permission_user_ids", default=[]),
        permission_menu_ids: List[str] = Form(alias="multi-select-permission_menu_ids", default=[]),
        db: Session = Depends(get_db)
    ):
    login_user = request.cookies.get("login")
    db_permission = get_permission_by_name(permission_name=permission_name, db=db)
    if db_permission:
        request.session["error"] = _("permission_already_exists")
        return RedirectResponse('/permissions/create', status_code=status.HTTP_400_BAD_REQUEST)

    new_permission = PermissionCreate(
        name=permission_name,
        description=permission_description,
        user_ids=", ".join(permission_user_ids),
        menu_ids=", ".join(permission_menu_ids),
        create_by=login_user,
        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    get_new_permission = create_permission(db=db, permission=new_permission)
    request.session["message"] = _("success_saved")

    for user_id in permission_user_ids:
        new_user = UpdateUserRole(
            id=user_id,
            user_role_id=get_new_permission.id,
            modify_by = login_user,
            modify_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        update_user_role(db, user=new_user)

    response = RedirectResponse('/permissions', status_code=status.HTTP_302_FOUND)
    return response

@router.get("/{id}/view")
async def read_permission_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    permission = get_permission(db, permission_id=int(id))
    if permission is None:
        request.session["error"] = _("permission_not_found")
        return RedirectResponse('/permissions', status_code=status.HTTP_404_NOT_FOUND)

    new_permission = object_to_json(permission)
    user_ids = new_permission['user_ids'].split(", ")
    user_name_list = get_user_name_by_id_list(db=db, user_ids=user_ids)
    new_permission['user_name_list'] = user_name_list

    menu_ids = new_permission['menu_ids'].split(", ")
    menu_name_list = get_menu_name_by_id_list(db=db, menu_ids=menu_ids)
    new_permission['menu_name_list'] = menu_name_list

    return templates.TemplateResponse("view/permissions/permission_view.html", {"request": request, "permission": new_permission})

@router.get("/{id}/modify")
async def edit_permission_by_id_get(request: Request, id: str, db: Session = Depends(get_db)):
    permission = get_permission(db, permission_id=int(id))
    if permission is None:
        request.session["error"] = _("permission_not_found")
        return RedirectResponse('/permissions', status_code=status.HTTP_404_NOT_FOUND)

    existed_user_ids = permission.user_ids.split(", ")
    existed_menu_ids = permission.menu_ids.split(", ")

    user_list = get_user_list(db=db)
    new_user_list = []
    for user in user_list:
        if str(user['id']) in existed_user_ids:
            user['checked'] = True
        else:
            user['checked'] = False
        new_user_list.append(user)

    menu_list = menu_list_id_name(db=db)
    new_menu_list = []
    for menu in menu_list:
        if str(menu['id']) in existed_menu_ids:
            menu['checked'] = True
        else:
            menu['checked'] = False
        new_menu_list.append(menu)

    new_permission = object_to_json(permission)
    return templates.TemplateResponse("view/permissions/permission_edit.html", {
        "request": request, "permission": new_permission,
        "user_list": new_user_list, "menu_list": new_menu_list,
    })

@router.post("/{id}/modify")
async def edit_permission_by_id_post(request: Request,
        permission_id: int = Form(...),
        permission_name: str = Form(...),
        permission_description: str = Form(...),
        permission_user_ids: List[str] = Form(alias="multi-select-permission_user_ids", default=[]),
        permission_menu_ids: List[str] = Form(alias="multi-select-permission_menu_ids", default=[]),
        db: Session = Depends(get_db)
    ):
    login_user = request.cookies.get("login")
    permission = get_permission(db, permission_id=int(permission_id))
    if permission is None:
        request.session["error"] = _("permission_not_found")
        return RedirectResponse('/permissions', status_code=status.HTTP_404_NOT_FOUND)

    new_permission = PermissionModify(
        id=permission_id,
        name=permission_name,
        description=permission_description,
        user_ids=", ".join(permission_user_ids),
        menu_ids=", ".join(permission_menu_ids),
        modify_by=login_user,
        modify_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    modify_permission(db, new_permission)
    request.session["message"] = _("success_saved")

    for user_id in permission_user_ids:
        print(user_id)
        new_user = UpdateUserRole(
            id=user_id,
            user_role_id=permission_id,
            modify_by=login_user,
            modify_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        update_user_role(db, user=new_user)

    return RedirectResponse('/permissions', status_code=status.HTTP_302_FOUND)

@router.post("/{id}/delete", response_model=Permission)
async def delete_permission(request: Request, id: str, db: Session = Depends(get_db)
):
    delete_permission_by_id(db, id)
    request.session["message"] = _("success_deleted")
    response = RedirectResponse('/permissions', status_code=status.HTTP_302_FOUND)
    return response

def get_permision_list():
    permissions = get_permissions(db=next(get_db()), skip=0, limit=100)
    permission_list = []
    for permission in permissions:
        permission_list.append({
            "id": permission.id,
            "name": permission.name,
        })
    return permission_list