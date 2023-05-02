import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from db.database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False,unique=True,)
    type = Column(String,nullable=False)
    update_time = Column(String,nullable=False)
    update_by = Column(String,nullable=False)
    status = Column(Integer,nullable=False)
