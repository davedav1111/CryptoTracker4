from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server import crud, schemas, auth, database
from fastapi.security import OAuth2PasswordRequestForm
from .database import get_db
import requests
from datetime import timedelta

# Instantiate FastAPI
app = FastAPI()

# User Registration Route
@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user is already registered
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create new user if not already registered
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: schemas.UserOut = Depends(auth.get_current_user)):
    return current_user

@app.get("/admin", response_model=schemas.UserOut)
def read_admin_data(current_user: schemas.UserOut = Depends(auth.get_current_admin_user)):
    return current_user

@app.get("/crypto/{coin_id}")
def get_crypto_price(coin_id: str, db: Session = Depends(get_db)):
    # Call CoinGecko API to get price
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Coin not found")
    price = response.json().get(coin_id, {}).get('usd')
    if price is None:
        raise HTTPException(status_code=404, detail="Price not found")
    return {"coin_id": coin_id, "price": price}

# Add Cryptocurrency to Portfolio
# @app.post("/portfolio/")
# def add_to_portfolio(portfolio: schemas.PortfolioCreate, db: Session = Depends(get_db)):
#     # Check if cryptocurrency is already in the user's portfolio
#     db_portfolio = crud.get_portfolio_by_uid_and_cid(db, uid=portfolio.uid, cid=portfolio.cid)
#     if db_portfolio:
#         raise HTTPException(status_code=400, detail="Cryptocurrency already in portfolio")
#     # Add cryptocurrency to portfolio
#     return crud.create_portfolio_entry(db=db, portfolio=portfolio)

# # Get User Portfolio
# @app.get("/portfolio/{uid}")
# def get_user_portfolio(uid: int, db: Session = Depends(get_db)):
#     portfolio = crud.get_portfolio_by_uid(db, uid=uid)
#     if not portfolio:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     return portfolio

# Create a Price Alert Subscription
# @app.post("/alerts/")
# def create_price_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
#     # Create a new price alert
#     return crud.create_alert_subscription(db=db, alert=alert)

# Get User Alerts
@app.get("/alerts/{uid}")
def get_user_alerts(uid: int, db: Session = Depends(get_db)):
    alerts = crud.get_alerts_by_uid(db, uid=uid)
    if not alerts:
        raise HTTPException(status_code=404, detail="No alerts found for this user")
    return alerts

# Add a New Wallet
# @app.post("/wallet/")
# def add_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db)):
#     # Add wallet to the user's profile
#     return crud.create_wallet(db=db, wallet=wallet)

# # Get User Wallets
# @app.get("/wallet/{uid}")
# def get_user_wallets(uid: int, db: Session = Depends(get_db)):
#     wallets = crud.get_wallets_by_uid(db, uid=uid)
#     if not wallets:
#         raise HTTPException(status_code=404, detail="No wallets found for this user")
#     return wallets

# # Record a Transaction
# @app.post("/transaction/")
# def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
#     # Log a new transaction for the user
#     return crud.create_transaction(db=db, transaction=transaction)

# # Get Transactions for User
# @app.get("/transaction/{uid}")
# def get_user_transactions(uid: int, db: Session = Depends(get_db)):
#     transactions = crud.get_transactions_by_uid(db, uid=uid)
#     if not transactions:
#         raise HTTPException(status_code=404, detail="No transactions found for this user")
#     return transactions

# Get Historical Price Data
@app.get("/price/history/{coin_id}")
def get_historical_price(coin_id: str):
    # Call CoinGecko API to get historical data
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")