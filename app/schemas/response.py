from pydantic import BaseModel, ConfigDict


class ResponseUserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UsersSchema(BaseModel):
    users: list[ResponseUserSchema]

    model_config = ConfigDict(from_attributes=True)
