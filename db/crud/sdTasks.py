from sqlalchemy.orm import Session

from db.schemas.sdTasks import SdTaskCreate, SdTaskModify
from db.models.sdTasks import SdTask


def get_sd_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SdTask).offset(skip).limit(limit).all()

def get_sd_tasks_by_user(db: Session, user: str, skip: int = 0, limit: int = 100):
    return db.query(SdTask).filter(SdTask.create_by == user).offset(skip).limit(limit).all()

def get_sd_tasks_by_user_type(db: Session, user: str, type: str, skip: int = 0, limit: int = 100):
    return db.query(SdTask).filter(SdTask.create_by == user and SdTask.type == type).offset(skip).limit(limit).all()


def get_sd_task(db: Session, sdTask_id: int):
    return db.query(SdTask).filter(SdTask.id == sdTask_id).first()


def get_sd_task_by_uuid(db: Session, sdTask_uid: str):
    return db.query(SdTask).filter(SdTask.uid == sdTask_uid).first()

def create_sdTask(db: Session, sdTask: SdTaskCreate):
    db_sdTask = SdTask(**sdTask.dict())
    db.add(db_sdTask)
    db.commit()
    db.refresh(db_sdTask)
    return db_sdTask

def modify_sdTask(db: Session, sdTask: SdTaskModify):
    db_sdTask = get_sd_task(db, sdTask_id=sdTask.id)
    db_sdTask.status = sdTask.status
    db_sdTask.content = sdTask.content
    db_sdTask.update_time = sdTask.update_time
    db.commit()
    db.refresh(db_sdTask)
    return db_sdTask

def delete_sd_task_by_id(db: Session, id: int):
    db_task = get_sd_task(db, id)
    db.delete(db_task)
    db.commit()

def delete_sd_task_by_uid(db: Session, uid: str):
    db_task = get_sd_task_by_uuid(db, uid)
    db.delete(db_task)
    db.commit()
