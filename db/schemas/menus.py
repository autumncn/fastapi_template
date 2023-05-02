from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr

class MenuBase(BaseModel):
    name: str
    path: str
    parent_id: int
    icon: str
    redirect: str
    title: str
    hidden: int
    type: str
    component: str
    sort: int
    level: int
    status: int


class MenuCreate(MenuBase):
    pass

class MenuModify(MenuBase):
    id: int

class Menu(MenuBase):
    id: int

