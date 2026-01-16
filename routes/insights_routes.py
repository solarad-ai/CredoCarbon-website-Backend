from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from auth import User, get_current_user
from utils import get_insights_data, save_insights_data


router = APIRouter(prefix="/api/insights", tags=["Insights"])


# ============ Pydantic Models for Insights ============

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


class GrowingSector(BaseModel):
    name: str
    growth: float
    unit: str = "%"


class RegionBreakdown(BaseModel):
    region: str
    share: float
    unit: str = "%"


class UpdateSubsectorRequest(BaseModel):
    registry_id: str
    sector_name: str
    subsector: Subsector


class AddSectorRequest(BaseModel):
    registry_id: str
    sector: Sector


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ============ GET Endpoints ============

@router.get("/all")
async def get_all_insights(current_user: User = Depends(get_current_user)):
    """Get all insights data."""
    try:
        data = get_insights_data()
        return data
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/carbon")
async def get_carbon_insights(current_user: User = Depends(get_current_user)):
    """Get carbon credits insights data."""
    data = get_insights_data()
    return data.get('carbonCredits', {})


@router.get("/rec")
async def get_rec_insights(current_user: User = Depends(get_current_user)):
    """Get REC insights data."""
    data = get_insights_data()
    return data.get('renewableEnergyCertificates', {})


@router.get("/carbon/{registry_id}")
async def get_carbon_registry_insights(registry_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific carbon registry's insights."""
    data = get_insights_data()
    for registry in data.get('carbonCredits', {}).get('registries', []):
        if registry.get('id') == registry_id:
            return registry
    raise HTTPException(status_code=404, detail=f"Carbon registry '{registry_id}' not found in insights")


@router.get("/rec/{registry_id}")
async def get_rec_registry_insights(registry_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific REC registry's insights."""
    data = get_insights_data()
    for registry in data.get('renewableEnergyCertificates', {}).get('registries', []):
        if registry.get('id') == registry_id:
            return registry
    raise HTTPException(status_code=404, detail=f"REC registry '{registry_id}' not found in insights")


# ============ UPDATE Summary ============

@router.put("/carbon/summary", response_model=MessageResponse)
async def update_carbon_summary(
    summary: Summary,
    current_user: User = Depends(get_current_user)
):
    """Update carbon credits summary."""
    data = get_insights_data()
    data['carbonCredits']['summary'] = summary.model_dump()
    save_insights_data(data)
    return MessageResponse(message="Carbon summary updated successfully")


@router.put("/rec/summary", response_model=MessageResponse)
async def update_rec_summary(
    summary: Summary,
    current_user: User = Depends(get_current_user)
):
    """Update REC summary."""
    data = get_insights_data()
    data['renewableEnergyCertificates']['summary'] = summary.model_dump()
    save_insights_data(data)
    return MessageResponse(message="REC summary updated successfully")


# ============ UPDATE/ADD Registry in Insights ============

@router.put("/carbon/registry/{registry_id}", response_model=MessageResponse)
async def update_carbon_registry_insights(
    registry_id: str,
    registry: InsightsRegistry,
    current_user: User = Depends(get_current_user)
):
    """Update a carbon registry's insights data."""
    data = get_insights_data()
    registries = data.get('carbonCredits', {}).get('registries', [])
    
    for i, r in enumerate(registries):
        if r.get('id') == registry_id:
            registries[i] = registry.model_dump()
            save_insights_data(data)
            return MessageResponse(message=f"Carbon registry '{registry.name}' insights updated")
    
    raise HTTPException(status_code=404, detail=f"Carbon registry '{registry_id}' not found in insights")


@router.put("/rec/registry/{registry_id}", response_model=MessageResponse)
async def update_rec_registry_insights(
    registry_id: str,
    registry: InsightsRegistry,
    current_user: User = Depends(get_current_user)
):
    """Update a REC registry's insights data."""
    data = get_insights_data()
    registries = data.get('renewableEnergyCertificates', {}).get('registries', [])
    
    for i, r in enumerate(registries):
        if r.get('id') == registry_id:
            registries[i] = registry.model_dump()
            save_insights_data(data)
            return MessageResponse(message=f"REC registry '{registry.name}' insights updated")
    
    raise HTTPException(status_code=404, detail=f"REC registry '{registry_id}' not found in insights")


@router.post("/carbon/registry", response_model=MessageResponse)
async def add_carbon_registry_insights(
    registry: InsightsRegistry,
    current_user: User = Depends(get_current_user)
):
    """Add a new carbon registry to insights."""
    data = get_insights_data()
    registries = data.get('carbonCredits', {}).get('registries', [])
    
    # Check if already exists
    for r in registries:
        if r.get('id') == registry.id:
            raise HTTPException(status_code=400, detail=f"Registry '{registry.id}' already exists in carbon insights")
    
    registries.append(registry.model_dump())
    save_insights_data(data)
    return MessageResponse(message=f"Carbon registry '{registry.name}' added to insights")


@router.post("/rec/registry", response_model=MessageResponse)
async def add_rec_registry_insights(
    registry: InsightsRegistry,
    current_user: User = Depends(get_current_user)
):
    """Add a new REC registry to insights."""
    data = get_insights_data()
    registries = data.get('renewableEnergyCertificates', {}).get('registries', [])
    
    for r in registries:
        if r.get('id') == registry.id:
            raise HTTPException(status_code=400, detail=f"Registry '{registry.id}' already exists in REC insights")
    
    registries.append(registry.model_dump())
    save_insights_data(data)
    return MessageResponse(message=f"REC registry '{registry.name}' added to insights")


@router.delete("/carbon/registry/{registry_id}", response_model=MessageResponse)
async def delete_carbon_registry_insights(
    registry_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a carbon registry from insights."""
    data = get_insights_data()
    registries = data.get('carbonCredits', {}).get('registries', [])
    
    for i, r in enumerate(registries):
        if r.get('id') == registry_id:
            del registries[i]
            save_insights_data(data)
            return MessageResponse(message=f"Carbon registry '{registry_id}' removed from insights")
    
    raise HTTPException(status_code=404, detail=f"Carbon registry '{registry_id}' not found in insights")


@router.delete("/rec/registry/{registry_id}", response_model=MessageResponse)
async def delete_rec_registry_insights(
    registry_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a REC registry from insights."""
    data = get_insights_data()
    registries = data.get('renewableEnergyCertificates', {}).get('registries', [])
    
    for i, r in enumerate(registries):
        if r.get('id') == registry_id:
            del registries[i]
            save_insights_data(data)
            return MessageResponse(message=f"REC registry '{registry_id}' removed from insights")
    
    raise HTTPException(status_code=404, detail=f"REC registry '{registry_id}' not found in insights")


# ============ Helper Functions ============

def recalculate_registry_totals(registry: dict) -> None:
    """Recalculate a registry's issued/retired totals from its subsectors."""
    total_issued = 0.0
    total_retired = 0.0
    has_retired = False
    
    for sector in registry.get('sectors', []):
        for subsector in sector.get('subsectors', []):
            issued = subsector.get('issued', 0) or 0
            retired = subsector.get('retired')
            total_issued += issued
            if retired is not None:
                total_retired += retired
                has_retired = True
    
    registry['issued'] = total_issued
    registry['retired'] = total_retired if has_retired else None


def recalculate_summary_totals(data: dict, category: str) -> None:
    """Recalculate summary totals for carbon or REC from all registries."""
    key = 'carbonCredits' if category == 'carbon' else 'renewableEnergyCertificates'
    registries = data.get(key, {}).get('registries', [])
    
    total_issued = 0.0
    total_retired = 0.0
    
    for registry in registries:
        issued = registry.get('issued', 0) or 0
        retired = registry.get('retired', 0) or 0
        total_issued += issued
        total_retired += retired
    
    data[key]['summary']['totalIssued'] = total_issued
    data[key]['summary']['totalRetired'] = total_retired


# ============ Subsector Updates ============

@router.put("/carbon/registry/{registry_id}/sector/{sector_name}/subsector/{subsector_name}", response_model=MessageResponse)
async def update_carbon_subsector(
    registry_id: str,
    sector_name: str,
    subsector_name: str,
    subsector: Subsector,
    current_user: User = Depends(get_current_user)
):
    """Update a specific subsector in carbon insights."""
    data = get_insights_data()
    
    for registry in data.get('carbonCredits', {}).get('registries', []):
        if registry.get('id') == registry_id:
            for sector in registry.get('sectors', []):
                if sector.get('name') == sector_name:
                    for i, sub in enumerate(sector.get('subsectors', [])):
                        if sub.get('name') == subsector_name:
                            sector['subsectors'][i] = subsector.model_dump()
                            # Recalculate registry totals from subsectors
                            recalculate_registry_totals(registry)
                            # Recalculate summary totals from all registries
                            recalculate_summary_totals(data, 'carbon')
                            save_insights_data(data)
                            return MessageResponse(message=f"Subsector '{subsector_name}' updated")
                    raise HTTPException(status_code=404, detail=f"Subsector '{subsector_name}' not found")
            raise HTTPException(status_code=404, detail=f"Sector '{sector_name}' not found")
    raise HTTPException(status_code=404, detail=f"Registry '{registry_id}' not found")


@router.put("/rec/registry/{registry_id}/sector/{sector_name}/subsector/{subsector_name}", response_model=MessageResponse)
async def update_rec_subsector(
    registry_id: str,
    sector_name: str,
    subsector_name: str,
    subsector: Subsector,
    current_user: User = Depends(get_current_user)
):
    """Update a specific subsector in REC insights."""
    data = get_insights_data()
    
    for registry in data.get('renewableEnergyCertificates', {}).get('registries', []):
        if registry.get('id') == registry_id:
            for sector in registry.get('sectors', []):
                if sector.get('name') == sector_name:
                    for i, sub in enumerate(sector.get('subsectors', [])):
                        if sub.get('name') == subsector_name:
                            sector['subsectors'][i] = subsector.model_dump()
                            # Recalculate registry totals from subsectors
                            recalculate_registry_totals(registry)
                            # Recalculate summary totals from all registries
                            recalculate_summary_totals(data, 'rec')
                            save_insights_data(data)
                            return MessageResponse(message=f"Subsector '{subsector_name}' updated")
                    raise HTTPException(status_code=404, detail=f"Subsector '{subsector_name}' not found")
            raise HTTPException(status_code=404, detail=f"Sector '{sector_name}' not found")
    raise HTTPException(status_code=404, detail=f"Registry '{registry_id}' not found")


# ============ Market Trends ============

@router.get("/trends")
async def get_market_trends(current_user: User = Depends(get_current_user)):
    """Get market trends data."""
    data = get_insights_data()
    return data.get('marketTrends', {})


@router.put("/trends/growing-sectors", response_model=MessageResponse)
async def update_growing_sectors(
    sectors: List[GrowingSector],
    current_user: User = Depends(get_current_user)
):
    """Update top growing sectors."""
    data = get_insights_data()
    data['marketTrends']['topGrowingSectors'] = [s.model_dump() for s in sectors]
    save_insights_data(data)
    return MessageResponse(message="Growing sectors updated successfully")


@router.put("/trends/regions", response_model=MessageResponse)
async def update_region_breakdown(
    regions: List[RegionBreakdown],
    current_user: User = Depends(get_current_user)
):
    """Update region breakdown."""
    data = get_insights_data()
    data['marketTrends']['regionBreakdown'] = [r.model_dump() for r in regions]
    save_insights_data(data)
    return MessageResponse(message="Region breakdown updated successfully")
