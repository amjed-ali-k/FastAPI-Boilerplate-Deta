import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, validator


class Token(BaseModel):
    access_token: str
    token_type: str


class Social(BaseModel):
    # Social Media Accounts
    instagram: str
    facebook: str
    twitter: str
    youtube: str
    telegram: str
    whatsapp: str


class AccountDetails(BaseModel):
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class UserActionsHistory(BaseModel):
    username: str
    time: str = datetime.datetime.now().isoformat()
    description: Optional[str] = None
    icon: Optional[str]
    type: str


class UserFields(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_number: Optional[int] = None
    address: Optional[str] = None
    state: Optional[str] = 'Kerala'
    country: Optional[str] = 'In'
    zip: Optional[int] = None
    gender: Optional[str] = 'Male'
    occupation: Optional[str] = None
    avatar: Optional[HttpUrl] = None
    designation: Optional[str] = None
    about: Optional[str] = None
    social: Optional[Social]
    badges: Optional[List]


class User(UserFields):
    key: Optional[str]
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = False
    roles: Optional[List] = ['User']
    accounts: Optional[AccountDetails]

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v


class UserInDB(User):
    hashed_password: str



class UserCreate(User):
    password: str
    repeat_password: Optional[str]


class UserEdit(UserFields):
    username: str
    password: str


class ChangePassword(BaseModel):
    username: str
    password: str
    new_password: str
    repeat_password: str
