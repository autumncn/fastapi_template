import datetime
import os
import time
from typing import List

from fastapi.encoders import jsonable_encoder
from fastapi.params import Form
from fastapi import Request
from fastapi import Depends, APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from dependencies import templates

from utils.WebsocketUtil import ConnectionManager
from logs.logger import logger

router = APIRouter()

manager = ConnectionManager()

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse("sample/ws.html",{"request": request})


@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")