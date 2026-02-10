from enum import Enum


class AuthHeader(str, Enum):
    WWW_AUTHENTICATE = "WWW-Authenticate"
    BEARER = "Bearer"


class TokenClaim(str, Enum):
    EXPIRY = "exp"
    USER_ID = "user_id"
    TOKEN_VERSION = "token_version"


class AuthRoute(str, Enum):
    TOKEN_URL = "login"
