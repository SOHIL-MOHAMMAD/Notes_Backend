from datetime import datetime, timedelta, timezone
from typing import Annotated, List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import get_db
from models.UserModel import User_model
from schema.UserSchema import Signup, Token, TokenData, signupResponse
from settings import setting

user_router = APIRouter(prefix='/user', tags=['user'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/signin')
password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt


def authenticate(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        data = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        user_id = data.get('id')
        user = db.query(User_model).filter(User_model.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found'
            )
        return user
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your token has expired'
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are unauthorized'
        )


@user_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=signupResponse)
def signup_user(body: Signup, db: Session = Depends(get_db)):
    username_exists = db.query(User_model).filter(User_model.username == body.username).first()
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username already exists'
        )

    email_exists = db.query(User_model).filter(User_model.email == body.email).first()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already exists'
        )

    hashed_password = get_password_hash(body.password)

    new_user = User_model(
        username=body.username,
        email=body.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@user_router.post('/signin', status_code=status.HTTP_200_OK, response_model=Token)
def signin_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Session = Depends(get_db)
):
    user = db.query(User_model).filter(User_model.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    exp_time = timedelta(minutes=int(setting.EXP_TIME))
    token = create_access_token(
        data={'id': user.id, 'username': user.username}, 
        expires_delta=exp_time
    )

    return Token(access_token=token, token_type="bearer")


@user_router.get('/list', response_model=List[signupResponse])
def userList(db: Session = Depends(get_db)):
    users = db.query(User_model).all()
    return users


@user_router.delete('/remove/{id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User_model).filter(User_model.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    db.delete(user)
    db.commit()
    return None