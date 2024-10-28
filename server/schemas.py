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

class UserOut(BaseModel):
    uid: int
    role: str  # Add role field
    time_registered: Optional[datetime]

    class Config:
        from_attributes = True
        # 自动将 datetime 转换为字符串格式
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

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
    gas_fee: Optional[float] = 0.0
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