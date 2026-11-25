from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class ComponentStatus(BaseModel):
    status: Literal["healthy", "degraded", "down"]
    latency_ms: float = Field(..., ge=0)
    message: str = "Operating normally"

class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "down"]
    version: str
    uptime_seconds: float = Field(..., ge=0)
    timestamp: datetime
    model_loaded: bool = True
    database: ComponentStatus