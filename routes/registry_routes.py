from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from auth import User, get_current_user
from models import (
    CarbonRegistry,
    RecRegistry,
    EtsRegistry,
    MessageResponse,
)
from utils import (
    get_registry_data,
    save_registry_data,
    calculate_totals,
    update_registry_in_list,
    add_registry_to_list,
    delete_registry_from_list,
)

router = APIRouter(prefix="/api/registries", tags=["Registries"])


# ============ GET Endpoints ============

@router.get("/all")
async def get_all_registries(current_user: User = Depends(get_current_user)):
    """Get all registry data (requires authentication)."""
    try:
        data = get_registry_data()
        return data
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/carbon")
async def get_carbon_registries(current_user: User = Depends(get_current_user)):
    """Get all carbon registries."""
    data = get_registry_data()
    return data.get('carbonRegistries', [])


@router.get("/rec")
async def get_rec_registries(current_user: User = Depends(get_current_user)):
    """Get all REC registries."""
    data = get_registry_data()
    return data.get('recRegistries', [])


@router.get("/ets")
async def get_ets_registries(current_user: User = Depends(get_current_user)):
    """Get all ETS registries."""
    data = get_registry_data()
    return data.get('etsRegistries', [])


@router.get("/carbon/{registry_id}")
async def get_carbon_registry(registry_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific carbon registry by ID."""
    data = get_registry_data()
    for registry in data.get('carbonRegistries', []):
        if registry.get('id') == registry_id:
            return registry
    raise HTTPException(status_code=404, detail=f"Carbon registry '{registry_id}' not found")


@router.get("/rec/{registry_id}")
async def get_rec_registry(registry_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific REC registry by ID."""
    data = get_registry_data()
    for registry in data.get('recRegistries', []):
        if registry.get('id') == registry_id:
            return registry
    raise HTTPException(status_code=404, detail=f"REC registry '{registry_id}' not found")


@router.get("/ets/{registry_id}")
async def get_ets_registry(registry_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific ETS registry by ID."""
    data = get_registry_data()
    for registry in data.get('etsRegistries', []):
        if registry.get('id') == registry_id:
            return registry
    raise HTTPException(status_code=404, detail=f"ETS registry '{registry_id}' not found")


# ============ CREATE Endpoints ============

@router.post("/carbon", response_model=MessageResponse)
async def create_carbon_registry(
    registry: CarbonRegistry,
    current_user: User = Depends(get_current_user)
):
    """Create a new carbon registry."""
    data = get_registry_data()
    
    # Check if registry ID already exists
    for r in data.get('carbonRegistries', []):
        if r.get('id') == registry.id:
            raise HTTPException(
                status_code=400,
                detail=f"Carbon registry with ID '{registry.id}' already exists"
            )
    
    add_registry_to_list(data['carbonRegistries'], registry.model_dump())
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"Carbon registry '{registry.name}' created successfully")


@router.post("/rec", response_model=MessageResponse)
async def create_rec_registry(
    registry: RecRegistry,
    current_user: User = Depends(get_current_user)
):
    """Create a new REC registry."""
    data = get_registry_data()
    
    for r in data.get('recRegistries', []):
        if r.get('id') == registry.id:
            raise HTTPException(
                status_code=400,
                detail=f"REC registry with ID '{registry.id}' already exists"
            )
    
    add_registry_to_list(data['recRegistries'], registry.model_dump())
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"REC registry '{registry.name}' created successfully")


@router.post("/ets", response_model=MessageResponse)
async def create_ets_registry(
    registry: EtsRegistry,
    current_user: User = Depends(get_current_user)
):
    """Create a new ETS registry."""
    data = get_registry_data()
    
    for r in data.get('etsRegistries', []):
        if r.get('id') == registry.id:
            raise HTTPException(
                status_code=400,
                detail=f"ETS registry with ID '{registry.id}' already exists"
            )
    
    add_registry_to_list(data['etsRegistries'], registry.model_dump())
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"ETS registry '{registry.name}' created successfully")


# ============ UPDATE Endpoints ============

@router.put("/carbon/{registry_id}", response_model=MessageResponse)
async def update_carbon_registry(
    registry_id: str,
    registry: CarbonRegistry,
    current_user: User = Depends(get_current_user)
):
    """Update a carbon registry."""
    data = get_registry_data()
    
    updated = update_registry_in_list(
        data['carbonRegistries'],
        registry_id,
        registry.model_dump()
    )
    
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Carbon registry '{registry_id}' not found"
        )
    
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"Carbon registry '{registry.name}' updated successfully")


@router.put("/rec/{registry_id}", response_model=MessageResponse)
async def update_rec_registry(
    registry_id: str,
    registry: RecRegistry,
    current_user: User = Depends(get_current_user)
):
    """Update a REC registry."""
    data = get_registry_data()
    
    updated = update_registry_in_list(
        data['recRegistries'],
        registry_id,
        registry.model_dump()
    )
    
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"REC registry '{registry_id}' not found"
        )
    
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"REC registry '{registry.name}' updated successfully")


@router.put("/ets/{registry_id}", response_model=MessageResponse)
async def update_ets_registry(
    registry_id: str,
    registry: EtsRegistry,
    current_user: User = Depends(get_current_user)
):
    """Update an ETS registry."""
    data = get_registry_data()
    
    updated = update_registry_in_list(
        data['etsRegistries'],
        registry_id,
        registry.model_dump()
    )
    
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"ETS registry '{registry_id}' not found"
        )
    
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"ETS registry '{registry.name}' updated successfully")


# ============ DELETE Endpoints ============

@router.delete("/carbon/{registry_id}", response_model=MessageResponse)
async def delete_carbon_registry(
    registry_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a carbon registry."""
    data = get_registry_data()
    
    deleted = delete_registry_from_list(data['carbonRegistries'], registry_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Carbon registry '{registry_id}' not found"
        )
    
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"Carbon registry '{registry_id}' deleted successfully")


@router.delete("/rec/{registry_id}", response_model=MessageResponse)
async def delete_rec_registry(
    registry_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a REC registry."""
    data = get_registry_data()
    
    deleted = delete_registry_from_list(data['recRegistries'], registry_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"REC registry '{registry_id}' not found"
        )
    
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"REC registry '{registry_id}' deleted successfully")


@router.delete("/ets/{registry_id}", response_model=MessageResponse)
async def delete_ets_registry(
    registry_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an ETS registry."""
    data = get_registry_data()
    
    deleted = delete_registry_from_list(data['etsRegistries'], registry_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"ETS registry '{registry_id}' not found"
        )
    
    data['totals'] = calculate_totals(data)
    save_registry_data(data)
    
    return MessageResponse(message=f"ETS registry '{registry_id}' deleted successfully")
