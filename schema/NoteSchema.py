from pydantic import BaseModel

class Note_Schema(BaseModel):
    id: int
    title : str
    description : str
    backgroundColor : str
    textColor  : str
  
class Note_UpdateSchema(BaseModel):
    title : str
    description : str
    backgroundColor : str 
    textColor  : str
  
