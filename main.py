from fastapi import FastAPI
from database import Base, engine
import models
from fastapi.middleware.cors import CORSMiddleware
from router.UserRouter import user_router
from router.NotesRouter import notes_router
Base.metadata.create_all(bind=engine)

origins = [
    "https://notes-desk-seven.vercel.app", 
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(user_router)
app.include_router(notes_router)  