import logging
from pymongo import MongoClient
from typing import List, Dict, Any
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class MongoDBDAO:
    def __init__(self, db):
        self.db = db
        self.prices_collection = db['prices']  # Single collection for MVP

    def init_db(self):
        """Initialize the database with a single collection for price data."""
        try:
            if "prices" not in self.db.list_collection_names():
                self.db.create_collection("prices")
            # Index for efficient queries by symbol, time_frame, and timestamp
            self.prices_collection.create_index([("symbol", 1), ("time_frame", 1), ("timestamp", -1)])
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_data(
        self,
        symbol: str,
        time_frame: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch price and indicator data for a symbol and time frame."""
        try:
            query = {"symbol": symbol, "time_frame": time_frame}
            if start_time:
                query["timestamp"] = {"$gte": start_time.isoformat()}
            if end_time:
                query["timestamp"] = query.get("timestamp", {})
                query["timestamp"]["$lte"] = end_time.isoformat()

            data = list(self.prices_collection.find(query).sort("timestamp", 1))
            for item in data:
                item["open"] = float(item.get("open", 0.0))
                item["high"] = float(item.get("high", 0.0))
                item["low"] = float(item.get("low", 0.0))
                item["close"] = float(item.get("close", 0.0))
                item["volume"] = float(item.get("volume", 0.0))
                item["r_1"] = float(item.get("r_1", 0.0))
                item["r_2"] = float(item.get("r_2", 0.0))
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise

    def insert_many(self, data: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple price/indicator records."""
        try:
            result = self.prices_collection.insert_many(data)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            raise

    def create_indicator(self, indicator: Dict[str, Any]) -> str:
        """Insert a single price/indicator record (for compatibility)."""
        try:
            result = self.prices_collection.insert_one(indicator)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating indicator: {e}")
            raise
