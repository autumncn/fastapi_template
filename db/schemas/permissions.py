from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr

class PermissionBase(BaseModel):
    pass

class PermissionCreate(PermissionBase):
    name: str
    description: str
    user_ids: str
    menu_ids: str
    create_by: str
    create_time: str


class PermissionModify(PermissionBase):
    id: int
    name: str
    description: str
    user_ids: str
    menu_ids: str
    modify_by: str
    modify_time: str

class Permission(PermissionBase):
    id: int
    name: str
    description: str
    user_ids: str
    menu_ids: str
    modify_by: str
    modify_time: str
    create_by: str
    create_time: str

    class Config:
        # arbitrary_types_allowed = True
        orm_mode = True
