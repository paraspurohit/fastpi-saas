from enum import Enum


class OTPPurpose(str, Enum):
    FORGOT_PASSWORD = "forgot_password"
    EMAIL_VERIFICATION = "email_verification"
