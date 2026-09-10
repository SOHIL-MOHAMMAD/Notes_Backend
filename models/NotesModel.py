from database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey

class Notes_model(Base):
  __tablename__ = 'notes'
  
  id = Column(Integer, primary_key= True, index=True)
  title = Column(String(250), nullable=False, index=True )
  description = Column(Text)
  backgroundColor = Column(String(255), default='#ffffff')
  textColor = Column(String,default='#111111')
  

  