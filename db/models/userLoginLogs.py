import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from db.database import Base

class UserLoginLog(Base):
    __tablename__ = "user_login_log"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,nullable=True)
    ip = Column(String)
    country_code = Column(String)
    ua = Column(String)
    login_time = Column(String,nullable=False)

