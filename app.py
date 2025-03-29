from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import asyncio
from settings import settings
from fetchers import get_flatland_fetcher, FlatlandFetcher
from processors import get_flatland_strategy, FlatlandStrategy
from models import FlatlandBacktestRequest, FlatlandBacktestResponse
from db import MongoDBDAO
from auth import validate_api_key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
def get_dao():
    from pymongo import MongoClient
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGODB_DB_NAME]
    dao = MongoDBDAO(db)
    dao.init_db()
    return dao

# Rate Limiting (simplified for MVP)
rate_limit_store = {}
lock = asyncio.Lock()

async def rate_limit(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=403, detail="API key required")
    current_time = datetime.now().timestamp()
    async with lock:
        if api_key not in rate_limit_store:
            rate_limit_store[api_key] = []
        rate_limit_store[api_key] = [ts for ts in rate_limit_store[api_key] if ts > current_time - settings.RATE_LIMIT_WINDOW]
        rate_limit_store[api_key].append(current_time)
        if len(rate_limit_store[api_key]) > settings.RATE_LIMIT_MAX:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

# Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to LineLand FlatLand API"}

@app.post("/api/v1/flatland-backtest", response_model=FlatlandBacktestResponse, response_class=HTMLResponse)
async def flatland_backtest(
    request: FlatlandBacktestRequest,
    strategy: FlatlandStrategy = Depends(get_flatland_strategy),
    dao: MongoDBDAO = Depends(get_dao),
    fetcher: FlatlandFetcher = Depends(get_flatland_fetcher),
    _ = Depends(validate_api_key),
    __ = Depends(rate_limit)
):
    try:
        # Fetch and store data if not already in DB
        existing_data = dao.get_data(request.symbol, "30m", request.start_time, request.end_time)
        if not existing_data:
            data = await fetcher.get_time_series(request.symbol, "30m", limit=48)  # ~24 hours
            if data:
                dao.prices.insert_many([{"symbol": request.symbol, "time_frame": "30m", **d} for d in data])

        strategy.symbol = request.symbol
        strategy.threshold = request.threshold
        result = strategy.backtest_last_signals(request.start_time, request.end_time)
        plot_html = strategy.visualize_trades()
        return HTMLResponse(content=plot_html) if plot_html else FlatlandBacktestResponse(**result)
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
