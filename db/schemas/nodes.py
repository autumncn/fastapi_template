import datetime
from typing import List, Optional, Union
from pydantic import BaseModel


class NodeBase(BaseModel):
    status: int

class NodeCreate(NodeBase):
    name: str
    type: str


class Node(NodeBase):
    id: int
    name: str
    type: str
    update_time: str
    update_by: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class NodeModify(NodeBase):
    id: int
    name: str
    type: str
    update_time: str
    update_by: str

class NodeStatusUpdate(NodeBase):
    id: int
    update_time: str
    update_by: str