from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic.types import conint



class StoryBase(BaseModel):
    title: str
    province: str
    short_story: str
    published: bool = True



class StoryCreate(StoryBase):
    pass


# tidak menampilkan password ke user ketika selesai dibuat
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# mengembalikan respon ke user
class Story(StoryBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class StoryOut(BaseModel):
    Story: Story
    likes: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str




class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token : str
    token_type : str


class TokenData(BaseModel):
    id: Optional[int] = None


class Likes(BaseModel):
    story_id: int
    dir: conint(le=1)