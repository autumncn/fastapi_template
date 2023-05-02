import datetime
from typing import List, Optional, Union
from pydantic import BaseModel


class UserLoginLogBase(BaseModel):
    user_id: int


class UserLoginLogCreate(UserLoginLogBase):
    ip: str
    country_code: str
    ua: str
    login_time: str


class UserLoginLog(UserLoginLogBase):
    id: int
    ip: str
    country_code: str
    ua: str
    login_time: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UserLoginLogModify(UserLoginLogBase):
    id: int
    ip: str
    country_code: str
    ua: str
    login_time: str

