from fastapi import Query

from jose import jwt, JWTError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def password_hash(password):
    return pwd_context.hash(password)

def verify_password(password, hashed_password):
    return pwd_context.verify(password,hashed_password)



def pagination(query, skip :int=Query(0,ge=0), limit:int=Query(0,ge=1)):
    return query.offset(skip).limit(limit).all()