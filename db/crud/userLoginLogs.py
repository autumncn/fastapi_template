from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.schemas.userLoginLogs import UserLoginLogCreate, UserLoginLogModify
from db.models.userLoginLogs import UserLoginLog


async def get_userLoginLogs(db: AsyncSession, skip: int = 0, limit: int = 100):
    return db.query(UserLoginLog).offset(skip).limit(limit).all()

async def get_userLoginLogs_by_user_id(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(UserLoginLog).filter(UserLoginLog.user_id == user_id).offset(skip).limit(limit).all()

async def get_userLoginLog(db: AsyncSession, userLoginLog_id: int):
    return db.query(UserLoginLog).filter(UserLoginLog.id == userLoginLog_id).first()

async def create_userLoginLog(db: AsyncSession, newUserLoginLog: UserLoginLogCreate):
    db_UserLoginLog = UserLoginLog(
        user_id=newUserLoginLog.user_id, ip=newUserLoginLog.ip, country_code=newUserLoginLog.country_code,
        ua=newUserLoginLog.ua, login_time=newUserLoginLog.login_time)
    db.add(db_UserLoginLog)
    db.commit()
    db.refresh(db_UserLoginLog)
    return db_UserLoginLog

async def modify_userLoginLog(db: AsyncSession, userLoginLog: UserLoginLogModify):
    db_UserLoginLog = get_userLoginLog(db, userLoginLog_id=userLoginLog.id)
    db_UserLoginLog.ip = UserLoginLog.ip
    db_UserLoginLog.country_code = UserLoginLog.country_code
    db_UserLoginLog.ua = UserLoginLog.ua
    db_UserLoginLog.login_time = UserLoginLog.login_time
    db.commit()
    db.refresh(db_UserLoginLog)
    return db_UserLoginLog

async def delete_userLoginLog_by_id(db: AsyncSession, id: int):
    db_task = get_userLoginLog(db, id)
    db.delete(db_task)
    db.commit()
