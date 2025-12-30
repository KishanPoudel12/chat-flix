from fastapi import status,HTTPException
from sqlalchemy.orm import Session
from models import User
from schemas.user import UserCreate, UserUpdate
from utils import  pagination , password_hash, verify_password

def get_users(db:Session, skip:int =0, limit:int =10):
    query= db.query(User)
    users= pagination(query, skip, limit)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users Not Found")
    return users

def get_user_by_id(db:Session, user_id:int):
    user = db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return user

def get_user_by_username(db:Session , username:str):
    users = db.query(User).filter(User.username == username).all()
    return users

def create_user(db:Session, data:UserCreate,image_url:str=None):
    #user exist check
    user_exist=db.query(User).filter(User.email==data.email).first()
    if user_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Already Exist")
    plain_password= data.password
    hashed_password=password_hash(plain_password)
    user_data= User(**data.model_dump(exclude={"password"}),hashed_password=hashed_password,user_profile=image_url)
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data



async def update_user(db:Session , data:UserUpdate, user_id:int ,image_url:str=None):
    user_to_update= get_user_by_id(db, user_id)
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")

    data_dict = data.model_dump(exclude_unset=True)

    password = data_dict.pop("password", None )
    if password:
        user_to_update.hashed_password= password_hash(password)
    if image_url:
        user_to_update.user_profile=image_url

    for key , value in data_dict.items():
        setattr(user_to_update, key , value)


    db.commit()
    db.refresh(user_to_update)
    return user_to_update



def delete_user(db:Session , user_id:int ):
    user_to_delete= get_user_by_id(db, user_id)
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")

    db.delete(user_to_delete)
    db.commit()
    return user_to_delete

