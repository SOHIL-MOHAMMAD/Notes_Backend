from fastapi import APIRouter, Depends ,HTTPException,status, Form , Query
from models.NotesModel import Notes_model
from schema.NoteSchema import Note_Schema, Note_UpdateSchema
from router.UserRouter import authenticate
from typing import List
from database import get_db
from sqlalchemy.orm import Session

notes_router = APIRouter(prefix='/note', tags=['notes'])

@notes_router.get('/list', response_model=List[Note_Schema], status_code=status.HTTP_200_OK)
def get_all_notes(db:Session=  Depends(get_db), current_user = Depends(authenticate)):
  notes = db.query(Notes_model).all()
  return notes

@notes_router.post('/add', response_model=Note_Schema, status_code=status.HTTP_201_CREATED)
def Add_notes(
  title : str = Form(...),
  description : str = Form(...),
  backgroundColor : str = Form('#ffffff'),
  textColor : str = Form('#111111'),
  db:Session = Depends(get_db),
  current_user = Depends(authenticate)
):
  
  new_note = Notes_model(
    title = title,
    description = description,
    backgroundColor = backgroundColor,
    textColor = textColor
  )
  
  db.add(new_note)
  db.commit()
  db.refresh(new_note)
  return new_note

@notes_router.put('/update/{id}', response_model=Note_Schema, status_code=status.HTTP_202_ACCEPTED)
def update_notes(id:int, body : Note_UpdateSchema, db : Session = Depends(get_db), current_user = Depends(authenticate)):
    result = db.query(Notes_model).filter(Notes_model.id == id).first()
  
    if result is None:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail= 'note not found'
      )
    
    result.title = body.title
    result.backgroundColor = body.backgroundColor
    result.description = body.description
    result.textColor = body.textColor
  
    db.commit()
    db.refresh(result)
    return result
  
@notes_router.get('/list/{id}', response_model=Note_Schema, status_code=status.HTTP_200_OK)
def get_single_note(id : int, db:Session = Depends(get_db)):
  note = db.query(Notes_model).filter(Notes_model.id == id).first()
  return note

@notes_router.delete('/remove/{id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_note(id:int, db:Session = Depends(get_db), current_user = Depends(authenticate)):
  note = db.query(Notes_model).filter(Notes_model.id == id).first()
  if not note:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='note not found'
    )
  
  db.delete(note)
  db.commit()
  return note

@notes_router.get('/search',response_model=List[Note_Schema])
def search_note(q:str = Query(None, min_length=1), db:Session = Depends(get_db)):
  
  if not q:
    return db.query(Notes_model).all()
    
  search_item = f"%{q}%"
  result = db.query(Notes_model).filter(Notes_model.title.ilike(search_item)).all()
  
  return result