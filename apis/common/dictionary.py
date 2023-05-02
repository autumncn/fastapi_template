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

from db.crud.dictionary import get_dictionary, create_dictionary, get_dictionary, delete_dictionary_by_id, modify_dictionary, get_dictionary_by_name, get_dictionarys
from db.database import get_db
from db.schemas.items import ItemCreate, Item
from db.schemas.dictionary import DictionaryCreate, Dictionary, DictionaryModify
from logs.logger import logger
from utils.JsonUtil import object_to_json
from utils.ResponseUtil import JsonResponse

router = APIRouter()

@router.get("/", response_model=List[Dictionary])
def read_dictionary_list(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dictionary = get_dictionarys(db, skip=skip, limit=limit)
    new_dictionary = DictionaryCreate
    return templates.TemplateResponse("view/dictionary/dictionary.html", {"request": request, "dictionary_list": dictionary, "new_dictionary": new_dictionary})

@router.get("/create", response_model=Dictionary)
def create_dictionary_get(request: Request, db: Session = Depends(get_db)):
    new_dictionary = DictionaryCreate
    return templates.TemplateResponse("view/dictionary/dictionary_create.html", {"request": request, "new_dictionary": new_dictionary})

@router.post("/create", response_model=Dictionary)
async def create_dictionary_post(request: Request,
        dictionary_name: str = Form(...),
        dictionary_value: str = Form(...),
        dictionary_type: Optional[str] = Form(...),
        db: Session = Depends(get_db)
):
    db_dictionary = get_dictionary_by_name(dictionary_name=dictionary_name, db=db)
    if db_dictionary:
        request.session["error"] = _("dictionary_already_exists")
        return RedirectResponse('/dictionary/create', status_code=status.HTTP_400_BAD_REQUEST)

    new_dictionary = DictionaryCreate(
        name=dictionary_name,
        value=dictionary_value,
        type=dictionary_type,
    )

    create_dictionary(db=db, dictionary=new_dictionary)
    request.session["message"] = _("success_saved")

    response = RedirectResponse('/dictionary', status_code=status.HTTP_302_FOUND)
    return response

@router.get("/{id}/view")
async def read_dictionary_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    dictionary = get_dictionary(db, dictionary_id=int(id))
    if dictionary is None:
        request.session["error"] = _("dictionary_not_found")
        return RedirectResponse('/dictionary', status_code=status.HTTP_404_NOT_FOUND)

    new_dictionary = object_to_json(dictionary)
    return templates.TemplateResponse("view/dictionary/dictionary_view.html", {"request": request, "dictionary": new_dictionary})

@router.get("/{id}/modify")
async def edit_dictionary_by_id_get(request: Request, id: str, db: Session = Depends(get_db)):
    dictionary = get_dictionary(db, dictionary_id=int(id))
    if dictionary is None:
        request.session["error"] = _("dictionary_not_found")
        return RedirectResponse('/dictionary', status_code=status.HTTP_404_NOT_FOUND)

    new_dictionary = object_to_json(dictionary)
    return templates.TemplateResponse("view/dictionary/dictionary_edit.html", {"request": request, "dictionary": new_dictionary})

@router.post("/{id}/modify")
async def edit_dictionary_by_id_post(request: Request,
        dictionary_id: str = Form(...),
        dictionary_name: str = Form(...),
        dictionary_value: str = Form(...),
        dictionary_type: Optional[str] = Form(...),
        db: Session = Depends(get_db)):
    dictionary = get_dictionary(db, dictionary_id=int(dictionary_id))
    if dictionary is None:
        request.session["error"] = _("dictionary_not_found")
        return RedirectResponse('/dictionary', status_code=status.HTTP_404_NOT_FOUND)

    new_dictionary = DictionaryModify(
        id=dictionary_id,
        name=dictionary_name,
        value=dictionary_value,
        type=dictionary_type,
    )

    modify_dictionary(db, new_dictionary)
    request.session["message"] = _("success_saved")

    return RedirectResponse('/dictionary', status_code=status.HTTP_302_FOUND)

@router.post("/{id}/delete", response_model=Dictionary)
async def delete_dictionary(request: Request, id: str, db: Session = Depends(get_db)
):
    delete_dictionary_by_id(db, id)
    request.session["message"] = _("success_deleted")
    response = RedirectResponse('/dictionary', status_code=status.HTTP_302_FOUND)
    return response
