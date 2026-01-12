from typing import List, Optional
from pydantic import BaseModel


# ============ Registry Data Models ============

class CarbonRegistry(BaseModel):
    id: str
    name: str
    fullName: Optional[str] = None
    symbol: str
    country: str
    type: str = "voluntary"
    issued: Optional[float] = None
    retired: Optional[float] = None
    unit: str = "tCO2e"
    records: Optional[int] = None
    logo: Optional[str] = None
    active: bool = True


class RecRegistry(BaseModel):
    id: str
    name: str
    fullName: Optional[str] = None
    symbol: str
    country: str
    type: str = "rec"
    issued: Optional[float] = None
    retired: Optional[float] = None
    unit: str = "MWh"
    records: Optional[int] = None
    active: bool = True


class EtsRegistry(BaseModel):
    id: str
    name: str
    fullName: Optional[str] = None
    symbol: str
    country: str
    type: str = "ets"
    active: bool = True


class Totals(BaseModel):
    carbon: dict
    rec: dict
    ets: dict
    totalRegistries: int
    totalCountries: int


class RegistryData(BaseModel):
    lastUpdated: str
    carbonRegistries: List[CarbonRegistry]
    recRegistries: List[RecRegistry]
    etsRegistries: List[EtsRegistry]
    totals: Totals


# ============ Insights Data Models ============

class Subsector(BaseModel):
    name: str
    issued: float
    retired: Optional[float] = None


class Sector(BaseModel):
    name: str
    subsectors: List[Subsector]


class InsightsRegistry(BaseModel):
    id: str
    name: str
    symbol: str
    issued: float
    retired: Optional[float] = None
    unit: str
    sectors: List[Sector]


class Summary(BaseModel):
    totalIssued: float
    totalRetired: float
    unit: str


class CategoryData(BaseModel):
    summary: Summary
    registries: List[InsightsRegistry]


class GrowingSector(BaseModel):
    name: str
    growth: float
    unit: str


class RegionBreakdown(BaseModel):
    region: str
    share: float
    unit: str


class MarketTrends(BaseModel):
    topGrowingSectors: List[GrowingSector]
    regionBreakdown: List[RegionBreakdown]


class InsightsData(BaseModel):
    lastUpdated: str
    description: str
    carbonCredits: CategoryData
    renewableEnergyCertificates: CategoryData
    marketTrends: MarketTrends


# ============ Request/Response Models ============

class UpdateCarbonRegistryRequest(BaseModel):
    registry: CarbonRegistry


class UpdateRecRegistryRequest(BaseModel):
    registry: RecRegistry


class UpdateEtsRegistryRequest(BaseModel):
    registry: EtsRegistry


class BulkUpdateRequest(BaseModel):
    carbonRegistries: Optional[List[CarbonRegistry]] = None
    recRegistries: Optional[List[RecRegistry]] = None
    etsRegistries: Optional[List[EtsRegistry]] = None


class MessageResponse(BaseModel):
    message: str
    success: bool = True
