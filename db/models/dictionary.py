# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, func

from db.database import Base

class Dictionary(Base):
    """ 系统路由 """
    __tablename__ = "config_dict"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    value = Column(String)
    type = Column(String)

