from sqlalchemy import Column, Integer, String
from database import Base

class User_model(Base):
  __tablename__ = 'user'
  
  id = Column(Integer, primary_key=True,index=True)
  username = Column(String(255), nullable=False)
  email = Column(String(255), nullable=False)
  password = Column(String, nullable=False)
  
  