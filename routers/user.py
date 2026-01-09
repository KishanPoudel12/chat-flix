from datetime import timedelta

from auth import get_current_active_user, guest_access_token, create_access_token
from cloudinary_util import upload_image
from fastapi import APIRouter, UploadFile,HTTPException,status,Form,Response
from fastapi.params import Depends
from sqlalchemy.orm import Session
from crud.user import get_users,get_user_by_id, delete_user, update_user,create_user
from database import get_db
from schemas.user import UserResponse, UserCreate, UserUpdate
from models.user import  User
import os
user_router= APIRouter(
    prefix="/users",
    tags=["User"]
)

@user_router.get("/", response_model=list[UserResponse])
async def read_all_users(db:Session=Depends(get_db), skip:int=0, limit:int =10,current_user:User=Depends(get_current_active_user)):
    if current_user.is_active:
        return get_users(db, skip, limit)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive User can't  Access ")


@user_router.get("/{user_id}",response_model=UserResponse)
async def read_single_user(user_id:int,db:Session=Depends(get_db), current_user:User=Depends(get_current_active_user)):
    if current_user.id!= user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cannot Access Others ")
    if current_user.is_active:
        return get_user_by_id(db, user_id)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive User can't  Access ")


#for guest ko lagi
@user_router.post("/guest")
async def create_guest_user(db:Session=Depends(get_db)):
    import uuid
    image_url = "_guest_"
    guest_email = f"guest_{uuid.uuid4().hex}@example.com"
    guest_username = f"guest_{uuid.uuid4().hex[:8]}"
    guest_password = uuid.uuid4().hex

    data=UserCreate(
        username=guest_username,
        email=guest_email,
        password=guest_password,
        is_guest=True
    )
    created_user=create_user(db,data=data,image_url=image_url)
    if not created_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Creation Unsuccessfull")
    access_token = guest_access_token(
        data={"sub": str(created_user.id), "is_guest": True}
    )


    return {
    "user": created_user,
    "access_token": access_token,
    "token_type": "bearer"
}



#for real users

@user_router.post("/create")
async def create_new_user(response:Response,username:str=Form(...), email:str = Form(...), password:str=Form(...), db:Session=Depends(get_db),image:UploadFile|None=None):
    image_url=None
    if image:
        try:
            image_url =  await upload_image(image)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image Upload Failed : {e}")
    data=UserCreate(
        username=username,
        email=email,
        password=password,
        is_guest=False
    )
    created_user=  create_user(db, data, image_url=image_url)
    if not created_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"user_id": created_user.id},
        expire_delta=access_token_expires)

    return {
        "access_token":access_token,
        "user":created_user
    }

@user_router.put("/{user_id}",response_model=UserResponse)
async  def update_existing_user(user_id:int ,username:str=Form(...), email:str = Form(...), password:str=Form(...), image:UploadFile| None=None, db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    if user_id!= current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cannot Update Other's Data")
    if image:
        try:
            image_url = await upload_image(image)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image Upload Failed : {e}")
    data=UserUpdate(
        username=username,
        email=email,
        password=password,
    )
    user_update= await update_user(db , data , user_id ,image_url)
    if not user_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return user_update

@user_router.delete("/{user_id}",response_model=UserResponse)
async def delete_existing_user(user_id:int , db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cannot Delete Other's Data")
    user_delete= delete_user(db, user_id)
    if not user_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User not Found")
    return user_delete
