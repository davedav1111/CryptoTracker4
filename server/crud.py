from sqlalchemy.orm import Session
from . import models, schemas, utils
from datetime import datetime, timezone

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        username=user.username,
        role=user.role,  # Handle role field
        time_registered=datetime.now(timezone.utc)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_alerts_by_uid(db: Session, uid: int):
    return db.query(models.AlertSubscription).filter(models.AlertSubscription.uid == uid).all()