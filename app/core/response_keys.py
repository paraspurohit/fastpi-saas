from enum import Enum


class ResponseKey(str, Enum):
    DETAIL = "detail"
    MESSAGE = "message"
    PASSWORD = "password"
    OTP = "otp"
    EXPIRES_IN = "expires_in"
    ACCESS_TOKEN = "access_token"
