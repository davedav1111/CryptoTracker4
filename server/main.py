from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from ..server import crud, models, schemas
from .database import SessionLocal, engine
import requests

# 创建数据库表（如果表还不存在的话）
models.Base.metadata.create_all(bind=engine)

# 实例化 FastAPI
app = FastAPI()

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 用户注册路由
@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 检查用户是否已经注册
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 如果没有，创建新用户
    return crud.create_user(db=db, user=user)

# 获取加密货币价格并保存到数据库
@app.get("/crypto/{coin_id}")
def get_crypto_price(coin_id: str, db: Session = Depends(get_db)):
    # 调用 CoinGecko API 获取价格
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url)
    
    # 如果 API 调用成功
    if response.status_code == 200:
        price_data = response.json()
        price_usd = price_data[coin_id]['usd']
        
        # 将价格保存到数据库
        crud.save_price(db, coin_id, price_usd)
        
        # 返回价格信息
        return {"coin_id": coin_id, "price_usd": price_usd}
    else:
        # 如果加密货币没有找到，返回404错误
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
