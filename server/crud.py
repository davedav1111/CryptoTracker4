# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

# 创建新用户
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        password=user.password,  # 实际项目中应使用哈希加密保存密码
        username=user.username,
        time_registered=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
# app/crud.py

# 查询用户是否已经存在，通过 email 查询
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

