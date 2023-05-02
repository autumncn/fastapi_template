from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True,nullable=False)
    email = Column(String,nullable=False,unique=True,index=True)
    hashed_password = Column(String,nullable=False)
    is_active = Column(Integer(),default=1)
    is_superuser = Column(Integer(),default=0)
    language = Column(String,nullable=False,default="en")
    create_by = Column(String)
    create_time = Column(String)
    modify_by = Column(String)
    modify_time = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    deleted = Column(Integer(),default=0)
    date_entered = Column(String)
    user_role_id = Column(Integer())


    # jobs = relationship("Job",back_populates="owner")

