from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    # email: str
    pass


class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str
    is_active: int
    language: str
    create_by: str
    create_time: str
    first_name: str
    last_name: str
    user_role_id: int


class UserModify(UserBase):
    id: int
    username: str
    email: EmailStr
    is_active: int
    is_superuser: int
    modify_by: str
    modify_time: str
    first_name: str
    last_name: str
    user_role_id: int
    language: str

class UpdateUserRole(UserBase):
    id: int
    user_role_id: int
    modify_by: str
    modify_time: str

class UpdateUserLang(UserBase):
    id: int
    language: str
    modify_by: str
    modify_time: str

class UpdateUserLogin(UserBase):
    id: int
    date_entered: str

class User(UserBase):
    id: int
    username: str
    email: EmailStr
    is_active: int
    is_superuser: int
    create_by: str
    create_date: str
    modify_by: str
    modify_time: str
    first_name: str
    last_name: str
    user_role_id: int
    language: str

    class Config:
        # arbitrary_types_allowed = True
        orm_mode = True

class ShowUser(BaseModel):   #new
    username: str
    email: EmailStr
    is_active: int
    is_superuser: int
    create_by: str
    create_date: str
    modify_by: str
    modify_time: str
    first_name: str
    last_name: str
    user_role_id: int
    language: str

    class Config:  #tells pydantic to convert even non dict obj to json
        # arbitrary_types_allowed = True
        orm_mode = True