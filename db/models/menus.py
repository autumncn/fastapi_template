# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, func

from db.database import Base

class Menu(Base):
    """ 系统路由 """
    __tablename__ = "sys_menu"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    path = Column(String)
    parent_id = Column(Integer)
    icon = Column(String)
    redirect = Column(String)
    title = Column(String)
    hidden = Column(Integer)
    type = Column(String)
    component = Column(String)
    sort = Column(Integer)
    level = Column(Integer)
    status = Column(Integer)

