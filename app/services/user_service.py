from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.constants import RESET_PASSWORD_WINDOW_MINUTES
from app.schemas.response import ResponseUserSchema, UsersSchema
from app.utils.login_util import hash_password, verify_password
from app.utils.otp import generate_otp
from app.database.models import UserModel, OTPModel
from app.schemas.request import (
    OTPRequest,
    RegisterUserSchema,
    UpdatePasswordSchema,
    UserUpdateSchema,
    VerifyOTP,
    VerifyPasssword,
    OTPPurpose
)
from app.core.messages import Message
from app.core.response_keys import ResponseKey


class UserService:

    def create_user(self, user: RegisterUserSchema, db: Session):
        try:
            hashed_password = hash_password(user.password)
            user_model = user.model_dump()
            user_model.pop(ResponseKey.PASSWORD.value)
            new_user = UserModel(**user_model, hashed_password=hashed_password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return ResponseUserSchema.model_validate(new_user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Message.USER_ALREADY_EXISTS.value)

    def get_all_user(self, db: Session):
        users = db.query(UserModel).all()
        return UsersSchema(users=[ResponseUserSchema.model_validate(u) for u in users])

    def get_user(self, id: int, db: Session):
        user = db.query(UserModel).filter(UserModel.id == id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Message.USER_NOT_FOUND.value)
        return ResponseUserSchema.model_validate(user)

    def update_user(self, details: UserUpdateSchema, current_user: UserModel, db: Session):
        for key, value in details.model_dump(exclude_unset=True).items():
            setattr(current_user, key, value)
        db.commit()
        db.refresh(current_user)

    def delete_user(self, id: int, current_user: UserModel, db: Session):
        user = db.query(UserModel).get(id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Message.USER_NOT_FOUND.value)
        db.delete(user)
        current_user.token_version += 1
        db.commit()

    def update_password(self, password: UpdatePasswordSchema, db: Session, current_user: UserModel):
        if not verify_password(password.old_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Message.PASSWORDS_DO_NOT_MATCH.value)
        current_user.hashed_password = hash_password(password.new_password)
        current_user.token_version += 1
        db.commit()
        db.refresh(current_user)

    def forget_password(self, request_user: VerifyPasssword, db: Session):
        now = datetime.now(timezone.utc)
        otp_record = db.query(OTPModel).filter(
            OTPModel.email == request_user.email,
            OTPModel.purpose == OTPPurpose.FORGOT_PASSWORD.value,
            OTPModel.is_verified == True
        ).first()
        if not otp_record:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Message.OTP_REQUIRED.value)
        if (not otp_record.verified_at or otp_record.verified_at + timedelta(minutes=RESET_PASSWORD_WINDOW_MINUTES) < now):
            db.delete(otp_record)
            db.commit()
            raise HTTPException(status_code=status.HTTP_410_GONE, detail=Message.OTP_WINDOW_EXPIRED.value)
        user = db.query(UserModel).filter(UserModel.email == request_user.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Message.USER_ALREADY_EXISTS.value)
        user.hashed_password = hash_password(request_user.new_password)
        user.token_version += 1
        db.delete(otp_record)
        db.commit()
        db.refresh(user)
        return {ResponseKey.MESSAGE.value: Message.PASSWORD_RESET_SUCCESS.value}

    def send_otp(self, request_user: OTPRequest, db: Session):
        now = datetime.now(timezone.utc)
        user = db.query(UserModel).filter(UserModel.email == request_user.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=Message.USER_DOES_NOT_EXIST.value)
        try:
            purpose = OTPPurpose(request_user.purpose).value
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,detail=Message.INVALID_OTP_PURPOSE.value)
        if user.is_email_verified and purpose == OTPPurpose.EMAIL_VERIFICATION.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=Message.EMAIL_ALREADY_VERIFIED.value)
        if not user.is_email_verified and purpose == OTPPurpose.FORGOT_PASSWORD.value:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=Message.EMAIL_VERIFICATION_PURPOSE_MISMATCH)
        otp_record = db.query(OTPModel).filter(OTPModel.email == request_user.email).first()
        if otp_record and otp_record.otp_expiry and otp_record.otp_expiry > now:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=Message.OTP_ALREADY_SENT.value)
        otp = generate_otp()
        expiry = now + timedelta(minutes=5)
        if otp_record:
            otp_record.otp = otp
            otp_record.otp_expiry = expiry
            otp_record.purpose = purpose
            otp_record.is_verified = False
            otp_record.verified_at = None
        else:
            otp_record = OTPModel(
                email=request_user.email,
                purpose=purpose,
                otp=otp,
                otp_expiry=expiry
            )
            db.add(otp_record)
        db.commit()
        db.refresh(otp_record)
        return {
            ResponseKey.MESSAGE.value: Message.OTP_SENT.value,
            ResponseKey.OTP.value: otp,
            ResponseKey.EXPIRES_IN.value: 300
        }

    def verify_otp(self, request_user: VerifyOTP, db: Session):
        now = datetime.now(timezone.utc)
        otp_record = db.query(OTPModel).filter(
            OTPModel.email == request_user.email
        ).first()
        if not otp_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=Message.OTP_NOT_FOUND.value)
        if otp_record.otp != request_user.otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=Message.OTP_INVALID.value)
        if not otp_record.otp_expiry or otp_record.otp_expiry < now:
            raise HTTPException(status_code=status.HTTP_410_GONE,detail=Message.OTP_EXPIRED.value)
        otp_record.is_verified = True
        otp_record.verified_at = now
        user = db.query(UserModel).filter(UserModel.email == request_user.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=Message.USER_DOES_NOT_EXIST.value)
        if otp_record.purpose == OTPPurpose.EMAIL_VERIFICATION.value:
            user.is_email_verified = True
            db.delete(otp_record)
        db.commit()
        db.refresh(user)
        return {
            ResponseKey.MESSAGE.value: Message.OTP_VERIFIED.value
        }
