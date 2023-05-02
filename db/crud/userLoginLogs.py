from sqlalchemy.orm import Session

from db.schemas.userLoginLogs import UserLoginLogCreate, UserLoginLogModify
from db.models.userLoginLogs import UserLoginLog


def get_userLoginLogs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserLoginLog).offset(skip).limit(limit).all()

def get_userLoginLogs_by_user_id(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(UserLoginLog).filter(UserLoginLog.user_id == user_id).offset(skip).limit(limit).all()

def get_userLoginLog(db: Session, userLoginLog_id: int):
    return db.query(UserLoginLog).filter(UserLoginLog.id == userLoginLog_id).first()

def create_userLoginLog(db: Session, newUserLoginLog: UserLoginLogCreate):
    db_UserLoginLog = UserLoginLog(
        user_id=newUserLoginLog.user_id, ip=newUserLoginLog.ip, country_code=newUserLoginLog.country_code,
        ua=newUserLoginLog.ua, login_time=newUserLoginLog.login_time)
    db.add(db_UserLoginLog)
    db.commit()
    db.refresh(db_UserLoginLog)
    return db_UserLoginLog

def modify_userLoginLog(db: Session, userLoginLog: UserLoginLogModify):
    db_UserLoginLog = get_userLoginLog(db, userLoginLog_id=userLoginLog.id)
    db_UserLoginLog.ip = UserLoginLog.ip
    db_UserLoginLog.country_code = UserLoginLog.country_code
    db_UserLoginLog.ua = UserLoginLog.ua
    db_UserLoginLog.login_time = UserLoginLog.login_time
    db.commit()
    db.refresh(db_UserLoginLog)
    return db_UserLoginLog

def delete_userLoginLog_by_id(db: Session, id: int):
    db_task = get_userLoginLog(db, id)
    db.delete(db_task)
    db.commit()
