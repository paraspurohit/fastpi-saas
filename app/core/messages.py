from enum import Enum


class Message(str, Enum):
    BAD_LOGIN_REQUEST = "Incorrect username or password"
    WRONG_CREDS = "Wrong Credentials Provided"
    INVALID_CREDS = "Could not validate credentials"

    USER_ALREADY_EXISTS = "User already exists"
    USER_NOT_FOUND = "User not found"
    USER_DOES_NOT_EXIST = "User does not exist."

    EMAIL_NOT_VERIFIED = "Email not verified."
    EMAIL_ALREADY_VERIFIED = "Email already verified"
    EMAIL_VERIFICATION_PURPOSE_MISMATCH = "Email not verified. Change the purpose."

    PASSWORD_UPDATED = "Password updated successfully"
    PASSWORD_RESET_SUCCESS = "Password reset successful."
    PASSWORDS_DO_NOT_MATCH = "Given password does not match."

    OTP_REQUIRED = "OTP verification required before resetting password."
    OTP_WINDOW_EXPIRED = "Password reset window expired. Please request OTP again."
    OTP_ALREADY_SENT = "OTP already sent. Please wait before requesting a new one."
    OTP_SENT = "OTP sent successfully"
    OTP_NOT_FOUND = "OTP not found for this email"
    OTP_INVALID = "Invalid OTP"
    OTP_EXPIRED = "OTP expired"
    OTP_VERIFIED = "OTP verified successfully"

    INVALID_OTP_PURPOSE = "Invalid OTP purpose."

    DETAILS_UPDATED = "Updated Details Successfully"
