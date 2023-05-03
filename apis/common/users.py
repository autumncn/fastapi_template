import datetime
import time
from fastapi.params import Form
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
from starlette.responses import RedirectResponse, FileResponse
from fastapi import Request

from apis.common.permissions import get_permision_list
from db.crud.permissions import get_permission
from dependencies import templates
from starlette import status
from libs.fastapi_babel import _

from db.crud.users import get_user, create_user, get_user_by_email, get_users, delete_user_by_id, create_superuser, modify_user
from db.database import get_db
from db.schemas.users import UserCreate, User, UserModify
from logs.logger import logger
from utils.JsonUtil import object_to_json

router = APIRouter()

@router.get("/", response_model=List[User])
def read_user_list(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    print(users)
    new_user = UserCreate
    return templates.TemplateResponse("view/users/users.html", {"request": request, "user_list": users, "new_user": new_user})

@router.get("/create", response_model=User)
def create_user_get(request: Request, db: Session = Depends(get_db)):
    new_user = UserCreate
    user_role_list = get_permision_list()
    return templates.TemplateResponse("view/users/user_create.html", {"request": request, "new_user": new_user, "user_role_list": user_role_list})

@router.post("/create", response_model=User)
async def create_user_post(request: Request,
        email: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        user_type: str = Form(...),
        user_role_id: int = Form(...),
        user_lang: str = Form(...),
        db: Session = Depends(get_db)
):
    print(email, first_name, last_name, user_type, user_role_id, user_lang)
    login_user = request.cookies.get("login")
    db_user = get_user_by_email(email=email, db=db)
    if db_user:
        request.session["error"] = _("email_already_registered")
        # raise HTTPException(status_code=400, detail=_("email_already_registered"))
        return RedirectResponse('/users/create', status_code=status.HTTP_400_BAD_REQUEST)

    new_user = UserCreate(
        username=email,
        email=email,
        is_active=1,
        first_name=first_name,
        last_name=last_name,
        user_role_id=user_role_id,
        password="123456",
        language=user_lang,
        create_by=login_user,
        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    print(object_to_json(new_user))
    if user_type == "1":
        create_superuser(db=db, user=new_user)
    else:
        create_user(db=db, user=new_user)
    request.session["message"] = _("success_saved")

    response = RedirectResponse('/users', status_code=status.HTTP_302_FOUND)
    return response

@router.get("/{id}/view")
async def read_user_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    user = get_user(db, user_id=int(id))
    if user is None:
        # raise HTTPException(status_code=404, detail=_("user_not_found"))
        request.session["error"] = _("user_not_found")
        return RedirectResponse('/users', status_code=status.HTTP_404_NOT_FOUND)

    user_role_id = user.user_role_id
    user_permission = get_permission(db, permission_id=user_role_id)
    if user_permission is not None:
        user.permission_name = user_permission.name
    new_user = object_to_json(user)
    # print(new_user)
    return templates.TemplateResponse("view/users/user_view.html", {"request": request, "user": new_user})

@router.get("/{id}/modify")
async def edit_user_by_id_get(request: Request, id: str, db: Session = Depends(get_db)):
    user = get_user(db, user_id=int(id))
    if user is None:
        # raise HTTPException(status_code=404, detail=_("user_not_found"))
        request.session["error"] = _("user_not_found")
        return RedirectResponse('/users', status_code=status.HTTP_404_NOT_FOUND)

    if user.is_superuser is None:
        user.is_superuser = 0
    new_user = object_to_json(user)
    user_role_list = get_permision_list()
    return templates.TemplateResponse("view/users/user_edit.html", {"request": request, "user": new_user, "user_role_list": user_role_list})

@router.post("/{id}/modify")
async def edit_user_by_id_post(request: Request,
        user_id: str = Form(...),
        email: str = Form(...),
        user_status: str = Form(...),
        user_type: str = Form(...),
        user_lang: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        user_role_id: int = Form(...),
        db: Session = Depends(get_db)):
    login_user = request.cookies.get("login")
    user = get_user(db, user_id=int(user_id))
    if user is None:
        # raise HTTPException(status_code=404, detail=_("user_not_found"))
        request.session["error"] = _("user_not_found")
        return RedirectResponse('/users', status_code=status.HTTP_404_NOT_FOUND)

    if user_status == "1":
        is_active = 1
    else:
        is_active = 0
    if user_type == "1":
        is_superuser = 1
    else:
        is_superuser = 0
    new_user = UserModify(
        id=user_id,
        username=email,
        email=email,
        is_active=is_active,
        is_superuser=is_superuser,
        language=user_lang,
        first_name=first_name,
        last_name=last_name,
        user_role_id=user_role_id,
        modify_by=login_user,
        modify_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    )

    modify_user(db, new_user)
    request.session["message"] = _("success_saved")

    return RedirectResponse('/users', status_code=status.HTTP_302_FOUND)

@router.post("/{id}/delete", response_model=User)
async def delete_user(request: Request, id: str, db: Session = Depends(get_db)
):
    delete_user_by_id(db, id)
    request.session["message"] = _("success_deleted")
    response = RedirectResponse('/users', status_code=status.HTTP_302_FOUND)
    return response
