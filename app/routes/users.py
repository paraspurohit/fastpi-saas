from fastapi import Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.messages import Message
from app.core.response_keys import ResponseKey
from app.database.db import get_db
from app.database.models import UserModel
from app.services.user_service import UserService
from app.utils.login_util import get_current_user
from app.schemas.response import ResponseUserSchema, UsersSchema
from app.schemas.request import OTPRequest, RegisterUserSchema, UpdatePasswordSchema, UserUpdateSchema, VerifyOTP, VerifyPasssword


router = APIRouter(
    prefix='/users', 
    tags=['Users']
)

@router.post('/create')
def create_user(user: RegisterUserSchema, db: Annotated[Session, Depends(get_db)]):
    user: ResponseUserSchema =  UserService().create_user(user=user, db=db)
    return JSONResponse(content=user.model_dump(), status_code=status.HTTP_201_CREATED)

@router.post('/otp/request')
def send_otp(user: OTPRequest, db: Session = Depends(get_db)):
    return UserService().send_otp(request_user=user, db=db)

@router.post('/otp/verify')
def verify_otp(user: VerifyOTP, db: Session = Depends(get_db)):
    return UserService().verify_otp(request_user=user, db=db)

@router.get('/all')
def get_all_users(db: Annotated[Session, Depends(get_db)], current_user: UserModel = Depends(get_current_user)):
    users: UsersSchema =  UserService().get_all_user(db=db)
    return JSONResponse(content=users.model_dump(), status_code=status.HTTP_200_OK)

@router.get('/{id}')
def get_user(id:int , db: Annotated[Session, Depends(get_db)], current_user: UserModel = Depends(get_current_user)):
    user: ResponseUserSchema = UserService().get_user(id=id, db=db)
    return JSONResponse(content=user.model_dump(), status_code=status.HTTP_200_OK)

@router.delete('/delete/{id}')
def delete_user(id: int, db: Annotated[Session, Depends(get_db)], current_user: UserModel = Depends(get_current_user)):
    UserService().delete_user(id=id,current_user=current_user, db=db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/update-detail')
def update_user(user: UserUpdateSchema, db: Annotated[Session, Depends(get_db)], current_user: UserModel = Depends(get_current_user)):
    UserService().update_user(
        details=user, 
        current_user=current_user, 
        db=db
    )
    return JSONResponse(content={ResponseKey.DETAIL.value: Message.DETAILS_UPDATED.value}, status_code=status.HTTP_202_ACCEPTED) 

@router.patch('/update-password')
def update_password(password: UpdatePasswordSchema, db: Annotated[Session, Depends(get_db)], current_user: UserModel = Depends(get_current_user)):
    UserService().update_password(
        password=password,
        db=db,
        current_user=current_user
    )
    return JSONResponse(content={ResponseKey.DETAIL.value: Message.PASSWORD_UPDATED.value}, status_code=status.HTTP_202_ACCEPTED)

@router.patch('/forgot-password')
def forget_password_verify(user: VerifyPasssword, db: Session = Depends(get_db)):
    return UserService().forget_password(request_user=user,db=db)
