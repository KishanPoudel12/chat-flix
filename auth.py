import os
from datetime import timedelta
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import HTTPException, APIRouter, status, Response,Request
from sqlalchemy.orm import Session
from crud.user import get_user_by_id, get_user_by_username
from database import get_db
from schemas.user import UserResponse
from utils import  verify_password
from datetime import datetime
from typing import Annotated
from models import User
from schemas.token import Token
auth_router= APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="/auth/login")



def get_user_from_cookie(request:Request,db:Session =Depends(get_db) ):
    token = request.cookies.get("access_token")
    if not token :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Token Found on Users cookie")
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id= payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_user(db:Session, user_id:int):
    user= get_user_by_id(db,user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return user

def authenticate_user(db:Session, username:str, password:str):
    users= get_user_by_username(db, username)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    for user in users:
        if  verify_password(password, user.hashed_password):
            return user
    raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Password")


def create_access_token(data:dict , expire_delta:timedelta | None =None ):
    to_encode= data.copy()
    if expire_delta:
        expire = datetime.utcnow()+ expire_delta
    else:
        expire= datetime.utcnow()+ timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt= jwt.encode(to_encode,os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload=jwt.decode(token,os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id=payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user= get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception
    return user

def get_current_active_user(current_user:Annotated[User, Depends(get_current_user)]):
    if not getattr(current_user,"is_active", False):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return current_user


@auth_router.post("/login")
async def login_for_access_token(
  form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
  response:Response,
  db:Session=Depends(get_db),
):
  user= authenticate_user(db,form_data.username, form_data.password)
  if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
  access_token_expires=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))

  access_token= create_access_token(
        data={"user_id":user.id},
        expire_delta=access_token_expires)

  response.set_cookie(
      key="access_token",  # cookie name
      value=access_token,  # value with Bearer prefix
      httponly=True,  # prevent JS access for security
      max_age=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")) * 60,
      secure=False,  # set True in production with HTTPS
      samesite="lax",
      path="/"
  )
  return Token(access_token=access_token, token_type="bearer")

@auth_router.get("/me",response_model=UserResponse)
async def get_me(current_user:Annotated[User,Depends(get_current_active_user)]):
  return current_user

@auth_router.get("/debug-token")
async def get_token(token:Annotated[str | None ,Depends(oauth2_scheme)]):
  return {"token":token}



#guest user ko lagi auth
def guest_access_token(data:dict):
        to_encode= data.copy()
        expire= datetime.utcnow()+ timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30)))
        to_encode.update({"exp":expire})
        encoded_jwt= jwt.encode(to_encode,os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

        return encoded_jwt



#for Nonguest user only
def require_non_guest_user(current_user: User = Depends(get_current_active_user)):
    if current_user.is_guest:
        raise HTTPException(status_code=403, detail="Guest users cannot do this")
    return current_user