from pydantic import BaseModel, Field, EmailStr
from typing import List


class ColorSchema(BaseModel):
    id: int
    name: str
    hex: str

    class Config:
        schema_extra = {
            "example": {
                "id": 0,
                "name": "white",
                "hex": "#ffffff"
            }
        }


class PaletteSchema(BaseModel):
    id: int
    colors: List[ColorSchema]

    class Config:
        schema_extra = {
            "example": {
                "id": 0,
                "colors": [
                    {
                        "id": 0,
                        "name": "white",
                        "hex": "#ffffff"
                    }
                ]
            }
        }


class UserAuthSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "xxx@xyz.com",
                "password": "qwerty123"
            }
        }


class TokenData:
    access_token: str
    expire_time: int

    def __init__(self, access_token, expire_time):
        self.access_token = access_token
        self.expire_time = expire_time


class UserDBCreateRequest:
    email: str
    password: str
    token_data: TokenData

    def __init__(self, email, password, token_data):
        self.email = email
        self.password = password
        self.token_data = token_data


class UserDBResponse:
    email: str
    role: bool
    token_data: TokenData

    def __init__(self, email, role, token_data):
        self.email = email
        self.role = role
        self.token_data = token_data
