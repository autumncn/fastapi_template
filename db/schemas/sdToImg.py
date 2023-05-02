from typing import List, Optional, Union, Dict
from pydantic import BaseModel


class SdToImgBase(BaseModel):
    prompt: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = None

class SdToImg(SdToImgBase):
    id: int
    seed: Optional[int] = -1
    uri: Optional[str] = None
    step: Optional[int] = -1
    cfg: Optional[float] = -1
    controlnet_mode: Optional[str] = None
    create_by: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    content_new: Optional[str] = None

class SdToImgCreate(SdToImgBase):
    seed: Optional[int] = -1
    uri: Optional[str] = None
    step: Optional[int] = 25
    cfg: Optional[float] = 11.5
    controlnet_mode: Optional[str] = None
    create_time: Optional[str] = None
    create_by: Optional[str] = None

class SdToImgModify(SdToImgBase):
    id: int
    uri: Optional[str] = None
    seed: Optional[int] = -1
    update_time: Optional[str] = None
    content_new: Optional[str] = None
