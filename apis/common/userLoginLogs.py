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

from db.crud.userLoginLogs import get_userLoginLog, delete_userLoginLog_by_id, get_userLoginLogs
from db.database import get_db
from db.schemas.items import ItemCreate, Item
from db.schemas.userLoginLogs import UserLoginLogCreate, UserLoginLog, UserLoginLogModify
from logs.logger import logger
from service.userService import get_user_email_id_map
from utils.JsonUtil import object_to_json
from utils.ResponseUtil import JsonResponse

router = APIRouter()

@router.get("/", response_model=List[UserLoginLog])
def read_userLoginLog_list(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    userLoginLogs = get_userLoginLogs(db, skip=skip, limit=limit)

    user_emails = get_user_email_id_map()
    userLoginLog_list = []
    for userLoginLog in userLoginLogs:
        user_email = user_emails.get(userLoginLog.user_id)
        if user_email is None:
            userLoginLog.user_email = '-'
        else:
            userLoginLog.user_email = user_emails.get(userLoginLog.user_id)
        userLoginLog_list.append(userLoginLog)
        # print(userLoginLog.user_email)
    return templates.TemplateResponse("view/userLoginLogs/userLoginLogs.html", {"request": request, "userLoginLog_list": userLoginLog_list})

@router.get("/{id}/view")
async def read_userLoginLog_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    userLoginLog = get_userLoginLog(db, userLoginLog_id=int(id))
    print(userLoginLog)
    if userLoginLog is None:
        request.session["error"] = _("userLoginLog_not_found")
        return RedirectResponse('/access', status_code=status.HTTP_404_NOT_FOUND)

    user_emails = get_user_email_id_map()
    user_email = user_emails.get(userLoginLog.user_id)
    print(user_email)
    if user_email is None:
        userLoginLog.user_email = '-'
    else:
        userLoginLog.user_email = user_emails.get(userLoginLog.user_id)
    new_userLoginLog = object_to_json(userLoginLog)
    return templates.TemplateResponse("view/userLoginLogs/userLoginLog_view.html", {"request": request, "userLoginLog": new_userLoginLog})

@router.post("/{id}/delete", response_model=UserLoginLog)
async def delete_userLoginLog(request: Request, id: str, db: Session = Depends(get_db)
):
    delete_userLoginLog_by_id(db, id)
    request.session["message"] = _("success_deleted")
    response = RedirectResponse('/access', status_code=status.HTTP_302_FOUND)
    return response
