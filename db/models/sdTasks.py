import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from db.database import Base

class SdTask(Base):
    __tablename__ = "sd_task"

    id = Column(Integer,primary_key=True,index=True)
    status = Column(Integer,nullable=False)
    uid = Column(String,nullable=False)
    type = Column(String,nullable=False)
    create_by = Column(String,nullable=False,default="system")
    create_time = Column(String,nullable=False,default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    update_time = Column(String,nullable=False)
    content = Column(String,nullable=False)
