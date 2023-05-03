import datetime
import time
from fastapi.params import Form
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
from starlette.responses import RedirectResponse, FileResponse
from fastapi import Request
from libs.fastapi_babel import _

from db.crud.sdTasks import get_sd_tasks, delete_sd_task_by_id, modify_sdTask, get_sd_task
from db.schemas.sdTasks import SdTask
from db.schemas.sdTasks import SdTaskCreate, SdTaskModify
from dependencies import templates
from starlette import status

from db.database import get_db
from logs.logger import logger
from utils.JsonUtil import object_to_json

router = APIRouter()

@router.get("/", response_model=List[SdTask])
def read_task_list(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = get_sd_tasks(db, skip=skip, limit=limit)
    new_task = SdTaskCreate
    return templates.TemplateResponse("view/tasks/tasks.html", {"request": request, "task_list": tasks, "new_task": new_task})

@router.get("/{id}/view")
async def read_task_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    task = get_sd_task(db, sdTask_id=int(id))
    if task is None:
        # raise HTTPException(status_code=404, detail=_("task_not_found"))
        request.session["error"] = _("task_not_found")
        return RedirectResponse('/tasks', status_code=status.HTTP_404_NOT_FOUND)

    new_task = object_to_json(task)
    return templates.TemplateResponse("view/tasks/task_view.html", {"request": request, "task": new_task})

@router.get("/{id}/modify")
async def edit_task_by_id_get(request: Request, id: str, db: Session = Depends(get_db)):
    task = get_sd_task(db, sdTask_id=int(id))
    if task is None:
        # raise HTTPException(status_code=404, detail=_("task_not_found"))
        request.session["error"] = _("task_not_found")
        return RedirectResponse('/tasks', status_code=status.HTTP_404_NOT_FOUND)

    new_task = object_to_json(task)
    print(new_task)
    return templates.TemplateResponse("view/tasks/task_edit.html", {"request": request, "task": new_task})

@router.post("/{id}/modify")
async def edit_task_by_id_post(request: Request,
        task_id: str = Form(...),
        task_status: int = Form(...),
        db: Session = Depends(get_db)):
    task = get_sd_task(db, sdTask_id=int(task_id))
    if task is None:
        # raise HTTPException(status_code=404, detail=_("task_not_found"))
        request.session["error"] = _("task_not_found")
        return RedirectResponse('/tasks', status_code=status.HTTP_404_NOT_FOUND)

    new_task = SdTaskModify(
        id=task.id,
        status=task_status,
        content=task.content,
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    modify_sdTask(db, new_task)
    request.session["message"] = _("success_saved")

    return RedirectResponse('/tasks', status_code=status.HTTP_302_FOUND)

@router.post("/{id}/delete", response_model=SdTask)
async def delete_task(request: Request, id: str, db: Session = Depends(get_db)):
    delete_sd_task_by_id(db, int(id))
    request.session["message"] = _("success_deleted")

    response = RedirectResponse('/tasks', status_code=status.HTTP_302_FOUND)
    return response
