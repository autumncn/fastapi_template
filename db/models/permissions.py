from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True,nullable=False)
    description = Column(String,nullable=False)
    user_ids = Column(String)
    menu_ids = Column(String)
    create_by = Column(String)
    create_time = Column(String)
    modify_by = Column(String)
    modify_time = Column(String)

