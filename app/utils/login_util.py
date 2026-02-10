import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash


from app.database.db import get_db
from app.database.models import UserModel
from app.config.config import setting
from app.core.auth_constants import TokenClaim, AuthHeader, AuthRoute
from app.core.response_keys import ResponseKey 
from app.core.messages import Message

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AuthRoute.TOKEN_URL.value)


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> str:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(token_version: int, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({TokenClaim.EXPIRY.value: expire})
    to_encode.update({TokenClaim.TOKEN_VERSION.value: token_version})
    encoded_jwt = jwt.encode(to_encode, setting.secret_key, algorithm=setting.algorithm)
    return {ResponseKey.ACCESS_TOKEN.value : encoded_jwt}

def verify_access_token(token: str, credentital_exception):
    try:
        decoded_token = jwt.decode(token, setting.secret_key, setting.algorithm)
        user_id = decoded_token.get(TokenClaim.USER_ID.value)
        token_version = decoded_token.get(TokenClaim.TOKEN_VERSION.value)
        if not user_id or token_version is None:
            raise credentital_exception
        return user_id, token_version
    except jwt.InvalidTokenError as e:
        raise credentital_exception
    except jwt.ExpiredSignatureError:
        raise credentital_exception

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentital_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail=Message.INVALID_CREDS.value,
        headers={AuthHeader.WWW_AUTHENTICATE.value: AuthHeader.BEARER.value}
    )
    user_id = verify_access_token(token, credentital_exception)
    current_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    return current_user

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=Message.INVALID_CREDS.value,headers={AuthHeader.WWW_AUTHENTICATE.value: AuthHeader.BEARER.value},)
    user_id, token_version = verify_access_token(token, credential_exception)
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise credential_exception
    if user.token_version != token_version:
        raise credential_exception
    if not user.is_active:
        raise credential_exception
    return user
