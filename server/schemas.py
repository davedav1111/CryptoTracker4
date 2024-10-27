# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    uid: int
    time_registered: Optional[datetime]

    class Config:
        from_attributes = True
        # 自动将 datetime 转换为字符串格式
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
     