import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from db.models.sdToImg import SdToImg
from db.schemas.sdToImg import SdToImgCreate, SdToImgModify


def get_img_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SdToImg).order_by(SdToImg.id.desc()).offset(skip).limit(limit).all()

def get_img_by_id(db: Session, id: int):
    img = db.query(SdToImg).filter(SdToImg.id == id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return img

def get_img_by_uri(db: Session, uri: str):
    img = db.query(SdToImg).filter(SdToImg.uri == uri).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return img

def get_img_by_create(db: Session, create_by: str, create_time: str):
    img = db.query(SdToImg).filter(SdToImg.create_by == create_by and SdToImg.create_time == create_time).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return img

def create_sdToImg(db: Session, sdToImg: SdToImgCreate):
    db_sdToImg = SdToImg(**sdToImg.dict())
    db.add(db_sdToImg)
    db.commit()
    db.refresh(db_sdToImg)
    return db_sdToImg

def modify_sdToImg(db: Session, sdToImg: SdToImgModify):
    db_sdToImg = get_img_by_id(db, id=sdToImg.id)
    db_sdToImg.uri = sdToImg.uri
    db_sdToImg.seed = sdToImg.seed
    db_sdToImg.content_new = sdToImg.content_new
    db_sdToImg.update_time = sdToImg.update_time
    db.commit()
    db.refresh(db_sdToImg)
    return db_sdToImg

def delete_img_by_id(db: Session, id: int):
    db_img = get_img_by_id(db, id)
    db.delete(db_img)
    db.commit()