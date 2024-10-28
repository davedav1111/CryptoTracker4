from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from server import crud, schemas
from .database import SessionLocal
import requests

# Instantiate FastAPI
app = FastAPI()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- User Routes ----

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# ---- Cryptocurrency Routes ----

@app.get("/crypto/{coin_id}")
def get_crypto_price(coin_id: str, db: Session = Depends(get_db)):
    """
    Retrieve current price of a cryptocurrency using the CoinGecko API.
    """
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        price_data = response.json()
        price_usd = price_data[coin_id]['usd']
        crud.save_price(db, coin_id, price_usd)
        return {"coin_id": coin_id, "price_usd": price_usd}
    else:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")

# ---- Portfolio Routes ----

@app.post("/portfolio/", response_model=schemas.PortfolioOut)
def add_to_portfolio(portfolio: schemas.PortfolioCreate, db: Session = Depends(get_db)):
    """
    Add a cryptocurrency to the user's portfolio.
    """
    db_portfolio = crud.get_portfolio_by_uid_and_cid(db, uid=portfolio.uid, cid=portfolio.cid)
    if db_portfolio:
        raise HTTPException(status_code=400, detail="Cryptocurrency already in portfolio")
    return crud.create_portfolio_entry(db=db, portfolio=portfolio)

@app.get("/portfolio/{uid}")
def get_user_portfolio(uid: int, db: Session = Depends(get_db)):
    """
    Retrieve the portfolio for a user.
    """
    portfolio = crud.get_portfolio_by_uid(db, uid=uid)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

# ---- Price Alert Routes ----

@app.post("/alerts/", response_model=schemas.AlertOut)
def create_price_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    """
    Create a new price alert for a user.
    """
    return crud.create_alert_subscription(db=db, alert=alert)

@app.get("/alerts/{uid}")
def get_user_alerts(uid: int, db: Session = Depends(get_db)):
    """
    Retrieve all alerts for a specific user.
    """
    alerts = crud.get_alerts_by_uid(db, uid=uid)
    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found for this user")
    return alerts

# Background scheduler to check price targets periodically
scheduler = BackgroundScheduler()

def check_price_alerts():
    """
    Function to check for price alerts in the background.
    """
    db = SessionLocal()
    try:
        crud.check_price_targets(db)
    finally:
        db.close()

# Add the job to the scheduler to run every 5 minutes
scheduler.add_job(check_price_alerts, "interval", minutes=5)
scheduler.start()

# Ensure scheduler stops when app shuts down
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

# ---- Wallet Routes ----

@app.post("/wallet/", response_model=schemas.WalletCreate)
def add_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db)):
    """
    Add a new wallet to the user's account.
    """
    return crud.create_wallet(db=db, wallet=wallet)

@app.get("/wallet/{uid}")
def get_user_wallets(uid: int, db: Session = Depends(get_db)):
    """
    Retrieve all wallets for a specific user.
    """
    wallets = crud.get_wallets_by_uid(db, uid=uid)
    if not wallets:
        raise HTTPException(status_code=404, detail="No wallets found for this user")
    return wallets

# ---- Transaction Routes ----

@app.post("/transaction/", response_model=schemas.TransactionCreate)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """
    Log a new transaction for the user, updating the portfolio and wallet balances accordingly.
    Positive position indicates a buy, and negative indicates a sell.
    """
    return crud.create_transaction(db=db, transaction=transaction)

@app.get("/transaction/{uid}")
def get_user_transactions(uid: int, db: Session = Depends(get_db)):
    """
    Retrieve all transactions for a user.
    """
    transactions = crud.get_transactions_by_uid(db, uid=uid)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")
    return transactions

# ---- Historical Price Data Route ----

@app.get("/price/history/{coin_id}")
def get_historical_price(coin_id: str):
    """
    Retrieve 30-day historical price data for a cryptocurrency from CoinGecko API.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
