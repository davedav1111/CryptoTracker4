from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas

# ---- User Management Functions ----

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database.
    """
    db_user = models.User(
        email=user.email,
        password=user.password,  # Note: In production, use hashed password storage
        username=user.username,
        time_registered=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user from the database by email.
    """
    return db.query(models.User).filter(models.User.email == email).first()

# ---- Portfolio Management Functions ----

def create_portfolio_entry(db: Session, portfolio: schemas.PortfolioCreate):
    """
    Add a cryptocurrency to the user's portfolio.
    """
    db_portfolio = models.Portfolio(
        uid=portfolio.uid,
        cid=portfolio.cid,
        quantity=portfolio.amount,
        time_created=datetime.utcnow()
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

def update_portfolio_quantity(db: Session, uid: int, cid: str, new_quantity: float):
    """
    Update the quantity of a cryptocurrency in the user's portfolio.
    """
    db_portfolio = get_portfolio_by_uid_and_cid(db, uid, cid)
    if db_portfolio:
        db_portfolio.quantity = new_quantity
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    return None

def delete_portfolio_entry(db: Session, uid: int, cid: str):
    """
    Remove a cryptocurrency from the user's portfolio.
    """
    db_portfolio = get_portfolio_by_uid_and_cid(db, uid, cid)
    if db_portfolio:
        db.delete(db_portfolio)
        db.commit()
        return True
    return False

# ---- Price Alert Management Functions ----

def create_alert_subscription(db: Session, alert: schemas.AlertCreate):
    """
    Create a new price alert subscription for a user.
    """
    db_alert = models.AlertSubscription(
        uid=alert.uid,
        cid=alert.cid,
        alert_type="price",
        time_subscribed=datetime.utcnow(),
        subscription_active=True
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    db_price_alert = models.PriceAlertSubscription(
        asid=db_alert.asid,
        threshold=alert.price_target
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

from datetime import datetime
from sqlalchemy.orm import Session
from . import models

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

def create_message(db: Session, uid: int, asid: int, message_type: str, body: str):
    """
    Create a new message for the user.
    """
    db_message = models.Message(
        uid=uid,
        asid=asid,
        message_type=message_type,
        body=body,
        time_sent=datetime.utcnow(),
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
def update_wallet_balance_on_transaction(db: Session, wid: int, cid: str, quantity_change: float):
    """
    Adjust the wallet balance for a specific cryptocurrency based on transaction quantity.
    If the wallet holds the cryptocurrency, adjust the balance. If not, create a new balance entry.
    
    quantity_change:
      - Positive for buy transactions.
      - Negative for sell transactions.
    """
    # Query for an existing balance of the cryptocurrency in the wallet
    wallet_balance = db.query(models.WalletBalance).filter(
        models.WalletBalance.wid == wid,
        models.WalletBalance.cid == cid
    ).first()
    
    if wallet_balance:
        # Update the existing balance
        wallet_balance.balance += quantity_change
        
        # Optionally, delete entry if balance is zero or below
        if wallet_balance.balance <= 0:
            db.delete(wallet_balance)
        else:
            db.commit()
            db.refresh(wallet_balance)
    else:
        # Create a new balance entry if buying and no entry exists
        if quantity_change > 0:
            new_wallet_balance = models.WalletBalance(
                wid=wid,
                cid=cid,
                balance=quantity_change
            )
            db.add(new_wallet_balance)
            db.commit()
            db.refresh(new_wallet_balance)

    db.commit()


def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    """
    Record a new transaction and update both portfolio and wallet balances based on position sign.
    Positive position indicates a buy; negative indicates a sell.
    """
    quantity_change = transaction.position if transaction.success else 0

    # Create the transaction record
    db_transaction = models.Transaction(
        uid=transaction.uid,
        wid=transaction.wid,
        cid=transaction.cid,
        cid_target=transaction.cid_target,
        ex_rate=transaction.ex_rate,
        position=transaction.position,
        network=transaction.network,
        gas_fee=transaction.gas_fee,
        success=transaction.success,
        time_transaction=datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # Update the portfolio and wallet balances if the transaction was successful
    if transaction.success:
        update_portfolio_on_transaction(db, transaction.uid, transaction.cid, quantity_change)
        update_wallet_balance_on_transaction(db, transaction.wid, transaction.cid, quantity_change)

    return db_transaction




def get_transactions_by_uid(db: Session, uid: int):
    """
    Retrieve all transactions for a specific user by UID.
    """
    return db.query(models.Transaction).filter(models.Transaction.uid == uid).all()

def update_portfolio_on_transaction(db: Session, uid: int, cid: str, quantity_change: float):
    """
    Update the user's portfolio based on a transaction. If the user already holds
    the cryptocurrency, adjust the quantity. If not, create a new portfolio entry.
    
    Parameters:
    - quantity_change: The amount to add (positive) or subtract (negative).
    """
    # Check if the user already has this cryptocurrency in their portfolio
    portfolio_entry = get_portfolio_by_uid_and_cid(db, uid, cid)

    if portfolio_entry:
        # Update existing portfolio quantity
        portfolio_entry.quantity += quantity_change
        
        # If the resulting quantity is zero or negative, consider removing the entry (optional)
        if portfolio_entry.quantity <= 0:
            db.delete(portfolio_entry)
        else:
            db.commit()
            db.refresh(portfolio_entry)
    else:
        # If no entry exists, create a new one (only for positive quantities)
        if quantity_change > 0:
            new_portfolio_entry = models.Portfolio(
                uid=uid,
                cid=cid,
                quantity=quantity_change,
                time_created=datetime.utcnow()
            )
            db.add(new_portfolio_entry)
            db.commit()
            db.refresh(new_portfolio_entry)

    # Commit changes to the database
    db.commit()

