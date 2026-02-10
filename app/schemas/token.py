from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    token_version: int = 0
