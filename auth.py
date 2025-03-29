import logging
from fastapi import Depends, HTTPException, Header
from typing import Dict
from db import MongoDBDAO
from settings import settings

logger = logging.getLogger(__name__)

class KeylandGatekeeper:
    def __init__(self, dao: MongoDBDAO):
        self.dao = dao
        self.api_keys_collection = dao.db["api_keys"]

    def init_keys(self):
        """Initialize the api_keys collection with a default free key if empty."""
        try:
            if "api_keys" not in self.dao.db.list_collection_names():
                self.dao.db.create_collection("api_keys")
            # Insert default free key if not present
            default_key = settings.API_KEY  # From .env, e.g., "flatland-free-test"
            if not self.api_keys_collection.find_one({"_id": default_key}):
                self.api_keys_collection.insert_one({
                    "_id": default_key,
                    "role": "free",
                    "description": "Default free access key for FlatLand MVP"
                })
            self.api_keys_collection.create_index([("role", 1)])
        except Exception as e:
            logger.error(f"Failed to initialize API keys: {e}")
            raise

    def validate_api_key(self, x_api_key: str = Header(...)) -> Dict[str, str]:
        """Validate the API key and return role info; only 'free' role for MVP."""
        try:
            key_data = self.api_keys_collection.find_one({"_id": x_api_key})
            if not key_data:
                raise HTTPException(status_code=403, detail="Invalid API key")
            if key_data["role"] != "free":
                # For MVP, enforce only 'free' role; log others but allow as free
                logger.warning(f"Key {x_api_key} has role {key_data['role']}—treating as 'free' for MVP")
            return {"role": "free"}  # Hardcode to free for simplicity
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            raise HTTPException(status_code=403, detail="API key validation failed")

def get_keyland_gatekeeper(dao: MongoDBDAO = Depends()):
    """Dependency to provide KeylandGatekeeper instance."""
    gatekeeper = KeylandGatekeeper(dao)
    gatekeeper.init_keys()  # Ensure default key exists
    return gatekeeper

def validate_api_key(auth: Dict[str, str] = Depends(lambda x_api_key=Header(...): get_keyland_gatekeeper().validate_api_key(x_api_key))):
    """FastAPI dependency for endpoint authentication."""
    return auth
