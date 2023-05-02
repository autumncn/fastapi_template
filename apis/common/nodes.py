import datetime
import time
from fastapi.params import Form
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
from starlette.responses import RedirectResponse, FileResponse
from fastapi import Request

from db.crud.nodes import get_nodes, get_nodes_by_name, create_node, get_nodes_type, get_nodes_by_status
from libs.fastapi_babel import _

from db.crud.nodes import get_nodes, delete_node_by_id, modify_node, get_node
from db.schemas.nodes import Node
from db.schemas.nodes import NodeCreate, NodeModify
from dependencies import templates
from starlette import status

from db.database import get_db
from db.schemas.items import ItemCreate, Item
from logs.logger import logger
from service.sdService import get_progress_image
from utils.JsonUtil import object_to_json
from utils.ResponseUtil import JsonResponse

router = APIRouter()

@router.get("/", response_model=List[Node])
def read_node_list(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    nodes = get_nodes(db, skip=skip, limit=limit)
    new_node = NodeCreate
    return templates.TemplateResponse("view/nodes/nodes.html", {"request": request, "node_list": nodes, "new_node": new_node})


@router.get("/create", response_model=Node)
def create_node_get(request: Request, db: Session = Depends(get_db)):
    new_node = NodeCreate
    return templates.TemplateResponse("view/nodes/node_create.html", {"request": request, "new_node": new_node})

@router.post("/create", response_model=Node)
async def create_node_post(request: Request,
        node_name: str = Form(...),
        node_type: str = Form(...),
        node_status: int = Form(...),
        db: Session = Depends(get_db)
):
    db_node = get_nodes_by_name(node_name=node_name, db=db)
    if db_node:
        # raise HTTPException(status_code=400, detail=_("node_already_added"))
        request.session["error"] = _("node_already_added")
        return RedirectResponse('/nodes/create', status_code=status.HTTP_302_FOUND)
    print(node_name, node_type, node_status)
    new_node = NodeCreate(
        name=node_name.strip(),
        status=node_status,
        type=node_type,
    )

    create_node(db=db, node=new_node)
    request.session["message"] = _("success_saved")

    return RedirectResponse('/nodes', status_code=status.HTTP_302_FOUND)


@router.get("/{id}/view")
async def read_node_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    node = get_node(db, node_id=int(id))
    if node is None:
        # raise HTTPException(status_code=404, detail=_("node_not_found"))
        request.session["error"] = _("node_not_found")
        return RedirectResponse('/nodes', status_code=status.HTTP_404_NOT_FOUND)

    new_node = object_to_json(node)
    return templates.TemplateResponse("view/nodes/node_view.html", {"request": request, "node": new_node})

@router.get("/{id}/check_status")
async def check_node_by_id(request: Request, id: str, db: Session = Depends(get_db)):
    print(id)
    node = get_node(db, node_id=int(id))
    if node is None:
        # raise HTTPException(status_code=404, detail=_("node_not_found"))
        request.session["error"] = _("node_not_found")
        return RedirectResponse('/nodes', status_code=status.HTTP_404_NOT_FOUND)

    node_name = node.name
    print(node_name)
    try:
        progress, eta_relative, current_image = get_progress_image(node_name)
        if progress == 0.0 and eta_relative == 0.0:
            node.status = 1  # 1:available
        else:
            node.status = 2  # 2:busy
    except Exception as e:
        node.status = -1  # -1:unavailable

    if node.update_by == None:
        node.update_by = request.cookies.get("login")

    new_node = NodeModify(
        id=node.id,
        status=node.status,
        name=node.name,
        type=node.type,
        update_by=node.update_by,
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    modify_node(db=db, node=new_node)

    request.session["message"] = _("updated_saved")
    return RedirectResponse('/nodes', status_code=status.HTTP_302_FOUND)

@router.get("/check_status_by_type")
async def check_node_by_id(request: Request, node_type: str, db: Session = Depends(get_db)):
    nodes = get_nodes_type(db, node_type=node_type)
    available_nodes = []
    for node in nodes:
        node_name = node.name
        try:
            progress, eta_relative, current_image = get_progress_image(node_name)
            if progress == 0.0 and eta_relative == 0.0:
                node.status = 1 # 1:available
                available_nodes.append(node_name)
            else:
                node.status = 2 # 2:busy
        except Exception as e:
                node.status = -1 # -1:unavailable

        if node.update_by == None:
            node.update_by = request.cookies.get("login")

        new_node = NodeModify(
            id=node.id,
            status=node.status,
            name=node.name,
            type=node.type,
            update_by=node.update_by,
            update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        modify_node(db=db, node=new_node)
    request.session["message"] = _("updated_saved")
    return RedirectResponse('/nodes', status_code=status.HTTP_302_FOUND)

@router.get("/{id}/modify")
async def edit_node_by_id_get(request: Request, id: str, db: Session = Depends(get_db)):
    node = get_node(db, node_id=int(id))
    if node is None:
        # raise HTTPException(status_code=404, detail=_("node_not_found"))
        request.session["error"] = _("node_not_found")
        return RedirectResponse('/nodes', status_code=status.HTTP_404_NOT_FOUND)

    new_node = object_to_json(node)
    return templates.TemplateResponse("view/nodes/node_edit.html", {"request": request, "node": new_node})

@router.post("/{id}/modify")
async def edit_node_by_id_post(request: Request,
        node_id: str = Form(...),
        node_name: str = Form(...),
        node_status: int = Form(...),
        node_type: str = Form(...),
        db: Session = Depends(get_db)):
    node = get_node(db, node_id=int(node_id))
    if node is None:
        request.session["error"] = _("node_not_found")
        return RedirectResponse('/nodes/' + str(node_id) + '/modify', status_code=status.HTTP_302_FOUND)
    dupl_node = get_nodes_by_name(node_name=node_name, db=db)
    if dupl_node is not None:
        print(dupl_node)
        print(node_id, dupl_node.id)
        if int(dupl_node.id) != int(node_id):
            request.session["error"] = _("duplicated_node_name_found")
            return RedirectResponse('/nodes/' + str(node_id) + '/modify', status_code=status.HTTP_302_FOUND)

            # raise HTTPException(status_code=404, detail=_("duplicated_node_name_found"))
    new_node = NodeModify(
        id=node.id,
        name=node_name.strip(),
        status=node_status,
        type=node_type,
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        update_by=request.cookies.get("login")
        )
    modify_node(db, new_node)
    request.session["message"] = _("success_saved")
    return RedirectResponse('/nodes', status_code=status.HTTP_302_FOUND)

@router.post("/{id}/delete", response_model=Node)
async def delete_node(request: Request, id: str, db: Session = Depends(get_db)):
    delete_node_by_id(db, int(id))
    request.session["message"] = _("success_deleted")
    response = RedirectResponse('/nodes', status_code=status.HTTP_302_FOUND)
    return response

def get_available_nodes(node_type: str):
    nodes = get_nodes_by_status(db=next(get_db()), node_status=1)
    for node in nodes:
        if node.type == node_type:
            return str(nodes[0].name)
    return None