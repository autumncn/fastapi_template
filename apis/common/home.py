import datetime
import time

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List

from starlette import status

from db import schemas, crud
from db.database import get_db
from dependencies import templates
from logs.logger import logger

router = APIRouter()

@router.get("/")
async def home(request: Request):
    # return templates.TemplateResponse("general_pages/homepage.html",{"request":request})
    return RedirectResponse('/dashboard', status_code=status.HTTP_302_FOUND)


@router.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("general_pages/homepage.html",{"request":request})

@router.get("/error_page/403")
async def error_404(request: Request):
    return templates.TemplateResponse("errors/error-403.html",{"request":request})