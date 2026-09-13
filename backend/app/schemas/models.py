from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DataPoint(BaseModel):
    time: float
    concentration: float


class AnalyzeRequest(BaseModel):
    data: List[DataPoint] = Field(..., description="Experimental (t, C_A) points")
    concentration_unit: str = "mol/L"
    time_unit: str = "s"
    smoothing_strength: float = Field(0.5, ge=0.0, le=1.0)
    n_search_min: float = -2.0
    n_search_max: float = 5.0
    autocatalytic_C_R0: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    service: str
