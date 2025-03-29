import aiohttp
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FlatlandFetcher:
    def __init__(self, twelve_data_api_key: str, rise_app_url: str):
        self.twelve_data_api_key = twelve_data_api_key
        self.rise_app_url = rise_app_url
        self.base_url = "https://api.twelvedata.com"

    async def get_time_series(self, symbol: str, interval: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch time series data from Twelve Data and mock RISE indicators."""
        url = f"{self.base_url}/time_series?symbol={symbol}&interval={interval}&outputsize={limit}&apikey={self.twelve_data_api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if "values" not in data:
                    logger.error(f"No data for {symbol}: {data.get('message', 'Unknown error')}")
                    return []
                result = [
                    {
                        "timestamp": v["datetime"],
                        "open": float(v["open"]),
                        "high": float(v["high"]),
                        "low": float(v["low"]),
                        "close": float(v["close"]),
                        "volume": float(v.get("volume", 0))
                    }
                    for v in data["values"]
                ]
                # Mock RISE indicators until real API is integrated
                for d in result:
                    d["r_1"] = float(350 + (hash(d["timestamp"]) % 150))  # Random 350-500
                    d["r_2"] = float(300 + (hash(d["timestamp"]) % 200))  # Random 300-500
                return result

def get_flatland_fetcher():
    from settings import settings
    return FlatlandFetcher(settings.TWELVE_DATA_API_KEY, settings.RISE_APP_URL)
