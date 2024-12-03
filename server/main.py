from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server import crud, schemas, auth, database
from fastapi.security import OAuth2PasswordRequestForm
from .database import get_db
import requests
from datetime import timedelta
from tenacity import retry, stop_after_attempt, wait_exponential

# Instantiate FastAPI
app = FastAPI()

# User Registration Route
@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if user is already registered
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create new user if not already registered
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate the user and return an access token.
    """
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
    """
    Retrieve the current authenticated user's information.
    """
    return current_user

@app.get("/admin", response_model=schemas.UserOut)
def read_admin_data(current_user: schemas.UserOut = Depends(auth.get_current_admin_user)):
    """
    Retrieve the current authenticated admin user's information.
    """
    return current_user

# @app.get("/crypto/{coin_id}")
# def get_crypto_price(coin_id: str, db: Session = Depends(get_db)):
#     """
#     Authenticate the user and return an access token.
#     """
#     # Call CoinGecko API to get price
#     url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
#     response = requests.get(url)
#     if response.status_code != 200:
#         raise HTTPException(status_code=404, detail="Coin not found")
#     price = response.json().get(coin_id, {}).get('usd')
#     if price is None:
#         raise HTTPException(status_code=404, detail="Price not found")
#     return {"coin_id": coin_id, "price": price}



from requests.exceptions import Timeout, RequestException

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_crypto_data(coin_id: str):
    """
    从 CoinGecko API 获取加密货币数据，带有重试机制和错误处理。
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 如果返回错误的 HTTP 状态码则抛出异常
        return response.json()
    except Timeout:
        raise HTTPException(
            status_code=504,
            detail=f"Request to CoinGecko timed out for coin_id: {coin_id}",
        )
    except RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch data from CoinGecko for coin_id {coin_id}: {str(e)}",
        )


import logging

# 初始化日志器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/crypto/{coin_id}")
def get_crypto_price(coin_id: str, db: Session = Depends(get_db)):
    """
    获取指定加密货币的详细价格信息，包括当前价格、市值、市值排名、24小时交易量等。
    """
    logger.info(f"Fetching data for coin_id: {coin_id}")
    try:
        data = fetch_crypto_data(coin_id)
        logger.info(f"Successfully fetched data for coin_id: {coin_id}")
    except HTTPException as e:
        logger.error(f"Error fetching data for coin_id {coin_id}: {e.detail}")
        raise
    market_data = data.get("market_data", {})
    price_info = {
        "coin_id": coin_id,
        "current_price": market_data.get("current_price", {}).get("usd"),
        "market_cap": market_data.get("market_cap", {}).get("usd"),
        "market_cap_rank": data.get("market_cap_rank"),
        "total_volume": market_data.get("total_volume", {}).get("usd"),
        "high_24h": market_data.get("high_24h", {}).get("usd"),
        "low_24h": market_data.get("low_24h", {}).get("usd"),
    }
    return price_info



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

#TODO: Fix the following routes

# @app.post("/alerts/", response_model=schemas.AlertOut)
# def create_price_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
#     """
#     Create a new price alert for a user.
#     """
#     return crud.create_alert_subscription(db=db, alert=alert)

# @app.get("/alerts/{uid}")
# def get_user_alerts(uid: int, db: Session = Depends(get_db)):
#     """
#     Retrieve all alerts for a specific user.
#     """
#     alerts = crud.get_alerts_by_uid(db, uid=uid)
#     if not alerts:
#         raise HTTPException(status_code=404, detail="No alerts found for this user")
#     return alerts

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
