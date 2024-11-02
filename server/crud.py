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

# ---- Portfolio Management Functions ----

def create_portfolio_entry(db: Session, portfolio: schemas.PortfolioCreate):
    """
    Add a cryptocurrency to the user's portfolio.
    """
    db_portfolio = models.Portfolio(
        uid=portfolio.uid,
        cid=portfolio.cid,
        quantity=portfolio.amount,
        time_created=datetime.now(timezone.utc)
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def get_portfolio_by_uid(db: Session, uid: int):
    """
    Retrieve all portfolio entries for a specific user by UID.
    """
    return db.query(models.Portfolio).filter(models.Portfolio.uid == uid).all()

def get_portfolio_by_uid_and_cid(db: Session, uid: int, cid: str):
    """
    Retrieve a specific portfolio entry by UID and CID.
    """
    return db.query(models.Portfolio).filter(
        models.Portfolio.uid == uid,
        models.Portfolio.cid == cid
    ).first()

def update_portfolio(db: Session, uid: int, cid: str, quantity_change: float):
    portfolio_entry = db.query(models.Portfolio).filter(models.Portfolio.uid == uid, models.Portfolio.cid == cid).first()
    
    if portfolio_entry:
        # Update existing portfolio quantity
        portfolio_entry.amount += quantity_change
        
        # If the resulting quantity is zero or negative, consider removing the entry (optional)
        if portfolio_entry.amount <= 0:
            delete_portfolio_entry(db, uid, cid)
        else:
            db.commit()
    else:
        # If no entry exists, create a new one (only for positive quantities)
        if quantity_change > 0:
            new_portfolio = models.Portfolio(uid=uid, cid=cid, amount=quantity_change, time_added=datetime.now(timezone.utc))
            db.add(new_portfolio)
            db.commit()
            db.refresh(new_portfolio)
            return new_portfolio

def delete_portfolio_entry(db: Session, uid: int, cid: str):
    portfolio_entry = db.query(models.Portfolio).filter(models.Portfolio.uid == uid, models.Portfolio.cid == cid).first()
    if portfolio_entry:
        db.delete(portfolio_entry)
        db.commit()
        return True
    return False
# ---- Price Alert Management Functions ----

def create_alert_subscription(db: Session, alert: schemas.AlertCreate):
    db_alert = models.AlertSubscription(
        uid=alert.uid,
        cid=alert.cid,
        alert_type="price",
        time_subscribed=datetime.now(timezone.utc),
        subscription_active=True
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    db_price_alert = models.PriceAlertSubscription(
        asid=db_alert.asid,
        threshold=alert.price_target,
        threshold_percentage=alert.threshold_percentage
    )
    db.add(db_price_alert)
    db.commit()
    db.refresh(db_price_alert)
    return db_alert

def get_alerts_by_uid(db: Session, uid: int):
    """
    Retrieve all active alerts for a specific user by UID.
    """
    return db.query(models.AlertSubscription).filter(models.AlertSubscription.uid == uid).all()

def deactivate_alert(db: Session, asid: int):
    """
    Deactivate an alert subscription.
    """
    db_alert = db.query(models.AlertSubscription).filter(models.AlertSubscription.asid == asid).first()
    if db_alert:
        db_alert.subscription_active = False
        db.commit()
        db.refresh(db_alert)
        return db_alert
    return None

def check_price_targets(db: Session):
    """
    Check if any cryptocurrency price is within 10% of the user's alert threshold.
    If so, create a notification message for the user.
    """
    alerts = db.query(models.PriceAlertSubscription, models.AlertSubscription, models.Price).join(
        models.AlertSubscription, models.PriceAlertSubscription.asid == models.AlertSubscription.asid
    ).join(
        models.Price, models.AlertSubscription.cid == models.Price.cid
    ).filter(models.AlertSubscription.subscription_active == True).all()

    for alert in alerts:
        threshold = float(alert.PriceAlertSubscription.threshold)
        current_price = float(alert.Price.current_price)
        
        # Check if price is within 10% of the target threshold
        if abs(current_price - threshold) / threshold <= 0.1:
            # Create a message to notify the user
            create_message(
                db=db,
                uid=alert.AlertSubscription.uid,
                asid=alert.AlertSubscription.asid,
                message_type="Price Alert",
                body=f"The price of {alert.AlertSubscription.cid} is within 10% of your target price.",
            )

#TODO: Implement message
def create_message(db: Session, uid: int, asid: int, message_type: str, body: str):
    """
    Create a new message for the user.
    """
    db_message = models.Message(
        uid=uid,
        asid=asid,
        message_type=message_type,
        body=body,
        time_sent=datetime.now(timezone.utc),
        read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# ---- Cryptocurrency Management Functions ----

def get_all_cryptocurrencies(db: Session):
    """
    Retrieve all cryptocurrencies available in the system.
    """
    return db.query(models.Cryptocurrency).all()

# ---- Transaction Management Functions ----

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    """
    Record a new transaction and update both portfolio and wallet balances based on position sign.
    Positive position indicates a buy; negative indicates a sell.
    """
    quantity_change = transaction.position if transaction.success else 0

    # Create the transaction record
    db_transaction = schemas.TransactionCreate(
        uid=transaction.uid,
        wid=transaction.wid,
        cid=transaction.cid,
        cid_target=transaction.cid_target,
        ex_rate=transaction.ex_rate,
        position=transaction.position,
        network=transaction.network,
        success=transaction.success,
        time_transaction=datetime.now(timezone.utc)
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # Update the portfolio and wallet balances if the transaction was successful
    if transaction.success:
        # Update the portfolio balance
        update_portfolio(db, transaction.uid, transaction.cid, quantity_change)
        # Send alert message
        create_message(
            db=db,
            uid=transaction.uid,
            asid=db_transaction.tid,  # Assuming tid is the transaction ID
            message_type="Transaction Alert",
            body=f"Transaction for {transaction.cid} has been processed successfully."
        )

    return db_transaction

def get_transactions_by_uid(db: Session, uid: int):
    """
    Retrieve all transactions for a specific user by UID.
    """
    return db.query(models.Transaction).filter(models.Transaction.uid == uid).all()

def get_transactions_by_uid_and_cid(db: Session, uid: int, cid: str):
    """
    Retrieve all transactions for a specific user and cryptocurrency.
    """
    return db.query(models.Transaction).filter(
        models.Transaction.uid == uid,
        models.Transaction.cid == cid
    ).all()
    
def get_transactions_by_wid(db: Session, wid: int):
    """
    Retrieve all transactions for a specific wallet by WID.
    """
    return db.query(models.Transaction).filter(models.Transaction.wid == wid).all()

def get_transactions_by_tid(db: Session, tid: str):
    """
    Retrieve a specific transaction by TID.
    """
    return db.query(models.Transaction).filter(models.Transaction.tid == tid).first()

# ---- Wallet Management Functions ----

def create_wallet(db: Session, wallet: schemas.WalletCreate):
    """
    Add a wallet to the user's profile.
    """
    db_wallet = models.Wallet(
        uid=wallet.uid,
        wname=wallet.wname,
        address=wallet.address,
        time_added=wallet.time_added,
        time_accessed=wallet.time_accessed
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def update_wallet(db: Session, wid: int, wallet: schemas.WalletUpdate):
    """
    Update the wallet name and last accessed time.
    """
    db_wallet = db.query(models.Wallet).filter(models.Wallet.wid == wid).first()
    if db_wallet:
        db_wallet.wname = wallet.wname
        db_wallet.time_accessed = wallet.time_accessed
        db.commit()
        db.refresh(db_wallet)
        return db_wallet
    return None

def get_wallets_by_uid(db: Session, uid: int):
    """
    Retrieve all wallets for a specific user by UID.
    """
    return db.query(models.Wallet).filter(models.Wallet.uid == uid).all()

def delete_wallet(db: Session, wid: int):
    """
    Remove a wallet from the user's profile.
    """
    db_wallet = db.query(models.Wallet).filter(models.Wallet.wid == wid).first()
    if db_wallet:
        db.delete(db_wallet)
        db.commit()
        return True
    return False