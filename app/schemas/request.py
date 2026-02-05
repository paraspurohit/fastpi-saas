from pydantic import BaseModel, EmailStr

from app.core.enums import OTPPurpose


class RegisterUserSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str 


class UserUpdateSchema(BaseModel):
    first_name: str
    last_name: str


class UpdatePasswordSchema(BaseModel):
    old_password: str
    new_password: str


class OTPRequest(BaseModel):
    email: EmailStr
    purpose: OTPPurpose


class VerifyPasssword(BaseModel):
    email: EmailStr
    new_password: str


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str
