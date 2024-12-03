# server/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = ""
    role: Optional[str] = "user"  # Add role field with a default value

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[str] = None  # Add role field

# class UserOut(BaseModel):
#     uid: int
#     role: str  # Add role field
#     time_registered: Optional[datetime]

#     class Config:
#         from_attributes = True
#         # 自动将 datetime 转换为字符串格式
#         json_encoders = {
#             datetime: lambda v: v.isoformat()

#         }
class UserOut(BaseModel):
    uid: int
    email: EmailStr
    username: Optional[str]
    role: str
    time_registered: Optional[datetime]

    class Config:
        orm_mode = True  # 允许从 ORM 对象中读取字段
        json_encoders = {
            datetime: lambda v: v.isoformat()  # 将 datetime 转换为 ISO 格式字符串
        }



class PriceOut(BaseModel):
    pid: int
    cid: str
    current_price: str
    market_cap: Optional[int]
    market_cap_rank: Optional[int]
    total_volume: Optional[int]
    high_24h: Optional[str]
    low_24h: Optional[str]
    price_change_24h: Optional[str]
    price_change_percentage_24h: Optional[str]
    market_cap_change_24h: Optional[int]
    time_stamp: datetime

    class Config:
        orm_mode = True  # 允许 Pydantic 从 ORM 对象中读取数据



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None

class PortfolioCreate(BaseModel):
    uid: int
    cid: str
    amount: float = 0.0
    
class PortfolioUpdate(BaseModel):
    amount: float
    
class PortfolioOut(PortfolioCreate):
    pid: int
    time_added: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AlertCreate(BaseModel):
    uid: int
    cid: str
    price_target: Optional[float] = 0.0
    threshold_percentage: Optional[float] = 0.0

class AlertOut(AlertCreate):    
    aid: int
    time_created: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
class WalletCreate(BaseModel):
    uid: int
    wname: Optional[str] = None
    address: str
    time_added: datetime
    time_accessed: Optional[datetime] = None

class WalletUpdate(BaseModel):
    wname: Optional[str] = None
    time_accessed: Optional[datetime] = None

class WalletOut(WalletCreate):
    wid: int
    address: str
    time_created: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TransactionCreate(BaseModel):
    uid: int
    wid: int
    cid: str
    cid_target: str
    ex_rate: float
    position: str
    network: str
    success: bool = False
    time_transaction: datetime
    
class TransactionUpdate(BaseModel):
    success: bool
    time_transaction: datetime

class TransactionOut(TransactionCreate):
    tid: int
    time_transaction: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }