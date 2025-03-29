from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional

class FlatlandBacktestRequest(BaseModel):
    symbol: str
    start_time: datetime
    end_time: datetime
    threshold: Optional[float] = 350.0
    distance_threshold: Optional[float] = 0.01

class FlatlandBacktestResponse(BaseModel):
    symbol: str
    trades: List[Dict[str, Any]]
    performance: Dict[str, Any]
