from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr

class DictionaryBase(BaseModel):
    name: str
    value: str
    type: str

class DictionaryCreate(DictionaryBase):
    pass

class DictionaryModify(DictionaryBase):
    id: int

class Dictionary(DictionaryBase):
    id: int

