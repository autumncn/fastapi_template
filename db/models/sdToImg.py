import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from db.database import Base

class SdToImg(Base):
    __tablename__ = "sd_to_img"

    id = Column(Integer,primary_key=True,index=True)
    prompt = Column(String,nullable=False)
    seed = Column(Integer,unique=True,nullable=False,default=-1)
    step = Column(Integer,default=25)
    cfg = Column(Float,default=11.5)
    controlnet_mode = Column(String,nullable=False)
    type = Column(String,nullable=False)
    uri = Column(String,nullable=False,unique=True)
    create_by = Column(String,nullable=False,default="system")
    create_time = Column(String,nullable=False,default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    update_time = Column(String,nullable=False)
    content = Column(String,nullable=False)
    content_new = Column(String,nullable=False)
