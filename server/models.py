# server/models.py
from sqlalchemy import Column, Index, Integer, String, Boolean, TIMESTAMP
from sqlalchemy import Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    uid = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # Add a role field with a default value
    access_token = Column(String, nullable=True)
    deactivated = Column(Boolean, default=False)
    time_registered = Column(TIMESTAMP)
    time_last_active = Column(TIMESTAMP)

class AlertSubscription(Base):
    __tablename__ = "alert_subscription"
    
    asid = Column(Integer, primary_key=True, index=True)
    uid = Column(Integer, index=True)
    cid = Column(String, index=True)
    alert_type = Column(String)
    time_subscribed = Column(TIMESTAMP)
    subscription_active = Column(Boolean, default=False)

class Cryptocurrency(Base):
    __tablename__ = "cryptocurrency"
    
    cid = Column(String, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String, unique=True, index=True)
    image_url = Column(String, nullable=True)
    circulating_supply = Column(String, nullable=True)
    total_supply = Column(String, nullable=True)
    max_supply = Column(String, nullable=True)
    ath = Column(String, nullable=True)
    ath_date = Column(TIMESTAMP, nullable=True)
    atl = Column(String, nullable=True)
    atl_date = Column(TIMESTAMP, nullable=True)
    last_updated = Column(TIMESTAMP, nullable=True)

class Message(Base):
    __tablename__ = "message"
    
    mid = Column(Integer, primary_key=True, index=True)
    uid = Column(Integer, index=True)
    asid = Column(Integer, nullable=True)
    message_type = Column(String)
    body = Column(String)
    time_sent = Column(TIMESTAMP)
    read = Column(Boolean, default=False)
    time_read = Column(TIMESTAMP, nullable=True)

class Portfolio(Base):
    __tablename__ = "portfolio"
    
    uid = Column(Integer, primary_key=True, index=True)
    cid = Column(String, primary_key=True, index=True)
    asid = Column(Integer, index=True)
    time_created = Column(TIMESTAMP, nullable=True)
    quantity = Column(String, nullable=True)

class Price(Base):
    __tablename__ = "price"
    
    pid = Column(Integer, primary_key=True, index=True)
    cid = Column(String, index=True)
    current_price = Column(String)
    market_cap = Column(Integer, nullable=True)
    market_cap_rank = Column(Integer, nullable=True)
    total_volume = Column(Integer, nullable=True)
    high_24h = Column(String, nullable=True)
    low_24h = Column(String, nullable=True)
    price_change_24h = Column(String, nullable=True)
    price_change_percentage_24h = Column(String, nullable=True)
    market_cap_change_24h = Column(Integer, nullable=True)
    time_stamp = Column(TIMESTAMP)

class PriceAlertSubscription(Base):
    __tablename__ = "price_alert_subscription"
    
    pasid = Column(Integer, primary_key=True, index=True)
    asid = Column(Integer, index=True)
    threshold = Column(String)

class Transaction(Base):
    __tablename__ = "transaction"
    
    tid = Column(Integer, primary_key=True, index=True)
    uid = Column(Integer, index=True)
    wid = Column(Integer, index=True)
    cid = Column(String, index=True)
    cid_target = Column(String, index=True)
    ex_rate = Column(String)
    position = Column(String)
    network = Column(String)
    gas_fee = Column(String)
    success = Column(Boolean)
    time_transaction = Column(TIMESTAMP)

class Wallet(Base):
    __tablename__ = "wallet"
    
    wid = Column(Integer, primary_key=True, index=True)
    uid = Column(Integer, index=True)
    wname = Column(String, nullable=True)
    address = Column(String, unique=True, index=True)
    time_added = Column(TIMESTAMP)
    time_accessed = Column(TIMESTAMP, nullable=True)

Index('idx_alert_subscription_uid', AlertSubscription.uid, AlertSubscription.cid, AlertSubscription.alert_type)
Index('idx_portfolio_uid_cid', Portfolio.uid, Portfolio.cid)
Index('idx_price_alert_asid', PriceAlertSubscription.asid)
Index('idx_price_cid_timestamp', Price.cid, Price.time_stamp)
Index('idx_transaction_uid_cid_time', Transaction.uid, Transaction.cid, Transaction.time_transaction)
Index('idx_wallet_uid_address', Wallet.uid, Wallet.address)