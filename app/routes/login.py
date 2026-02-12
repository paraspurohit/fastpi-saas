from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.messages import Message
from app.core.auth_constants import TokenClaim
from app.database.db import get_db
from app.database.models import UserModel
from app.schemas.token import Token
from app.utils.login_util import create_access_token, verify_password

router = APIRouter(prefix="/login", tags=["Login"])


@router.post("/")
def login(
    login_user: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(UserModel).filter(UserModel.email == login_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Message.BAD_LOGIN_REQUEST.value,
        )
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Message.EMAIL_NOT_VERIFIED.value,
        )
    if not verify_password(login_user.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=Message.WRONG_CREDS.value
        )
    user_dict = {TokenClaim.USER_ID.value: user.id}
    return Token(
        **create_access_token(token_version=user.token_version, data=user_dict)
    )
