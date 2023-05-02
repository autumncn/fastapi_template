import datetime
import os
import time
from typing import List

from fastapi.params import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse, FileResponse
from starlette.background import BackgroundTask

from db.crud.items import get_items, create_user_item, get_item
from db.database import get_db
from db.schemas.items import Item, ItemCreate
from dependencies import templates
from utils.JsonUtil import model_list, object_to_json
from logs.logger import logger
from libs.fastapi_babel import _

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_item_list(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    # return items
    new_item = ItemCreate
    return templates.TemplateResponse("view/items/items.html",{"request": request, "item_list": items, "new_item": new_item})

#
# @router.get("/id={id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: str):
#     return templates.TemplateResponse("view/items/stable_view.html", {"request": request, "id": id})

@router.get("/{id}/view")
async def read_task_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    item = get_item(db, item_id=int(id))
    if item is None:
        # raise HTTPException(status_code=404, detail=_("item_not_found"))
        request.session["error"] = _("item_not_found")
        return RedirectResponse('/items', status_code=status.HTTP_404_NOT_FOUND)

    new_item = object_to_json(item)
    return templates.TemplateResponse("view/items/item_view.html", {"request": request, "item": new_item})


@router.post("/create", response_model=Item)
async def create_item(request: Request,
    set_user_id: int = Form(...),
    set_title: str = Form(...),
    set_description: str = Form(...),
    db: Session = Depends(get_db)
):
    # print(set_user_id, set_title, set_description)
    new_item = ItemCreate(
            title=set_title,
            description=set_description
        )
    create_user_item(db=db, item=new_item, user_id=set_user_id)
    request.session["message"] = _("success_saved")

    response = RedirectResponse('/items', status_code=status.HTTP_302_FOUND)
    return response

@router.get("/download", response_model=List[Item])
def download_items(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    item_list = model_list(items)

    file_content = str(item_list)
    basedir = os.path.abspath(os.path.dirname(__file__))
    rootPath = basedir[:basedir.find('cn_server')+len('cn_server')]

    file_path = os.path.join(rootPath, 'temp', 'test.txt')
    with open(file_path, 'w') as f:
        f.write(file_content)
    return FileResponse(file_path, media_type='text/plain', filename='test.txt',background=BackgroundTask(lambda: os.remove(file_path)))


