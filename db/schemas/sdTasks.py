import datetime
from typing import List, Optional, Union
from pydantic import BaseModel


class SdTaskBase(BaseModel):
    status: int = None
    uid: str = None
    content: Optional[str] = None

class SdTaskCreate(SdTaskBase):
    pass


class SdTask(SdTaskBase):
    id: int
    create_by: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class SdTaskCreate(SdTaskBase):
    type: str = None
    create_time: Optional[str] = None
    create_by: Optional[str] = None

class SdTaskModify(SdTaskBase):
    id: int
    update_time: Optional[str] = None
