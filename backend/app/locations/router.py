from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Location, Campaign, User
from app.schemas import (
    LocationCreate, LocationUpdate, Location as LocationSchema, 
    PaginatedLocationResponse
)
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedLocationResponse)
async def get_locations(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    location_type: Optional[str] = Query(None),
    parent_location_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None)
):
    """Get locations for a campaign with optional filtering."""
    query = db.query(Location).filter(Location.campaign_id == campaign_id)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Location.name.ilike(search_term) |
            Location.description.ilike(search_term) |
            Location.history.ilike(search_term)
        )
    
    if location_type:
        query = query.filter(Location.type == location_type)
    
    if parent_location_id is not None:
        query = query.filter(Location.parent_location_id == parent_location_id)
    
    if status:
        query = query.filter(Location.status == status)
        
    if visibility:
        query = query.filter(Location.visibility == visibility)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    locations = query.order_by(Location.name).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": locations
    }

@router.post("/", response_model=LocationSchema)
async def create_location(
    campaign_id: int,
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Create a new location."""
    # Validate parent location if provided
    if location_data.parent_location_id:
        parent = db.query(Location).filter(
            Location.id == location_data.parent_location_id,
            Location.campaign_id == campaign_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent location not found in this campaign"
            )
    
    db_location = Location(
        **location_data.dict(),
        campaign_id=campaign_id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    
    return db_location

@router.get("/{location_id}", response_model=LocationSchema)
async def get_location(
    campaign_id: int,
    location_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Get a specific location."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.campaign_id == campaign_id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    return location

@router.put("/{location_id}", response_model=LocationSchema)
async def update_location(
    campaign_id: int,
    location_id: int,
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Update a location."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.campaign_id == campaign_id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    # Validate parent location if provided and changed
    if location_data.parent_location_id is not None:
        if location_data.parent_location_id != location.parent_location_id:
            # Can't be its own parent
            if location_data.parent_location_id == location_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Location cannot be its own parent"
                )
            
            # Check if parent exists in campaign
            parent = db.query(Location).filter(
                Location.id == location_data.parent_location_id,
                Location.campaign_id == campaign_id
            ).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent location not found in this campaign"
                )
    
    # Update only provided fields
    update_data = location_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)
    
    db.commit()
    db.refresh(location)
    
    return location

@router.delete("/{location_id}")
async def delete_location(
    campaign_id: int,
    location_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Delete a location."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.campaign_id == campaign_id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    # Check if location has child locations
    child_count = db.query(Location).filter(
        Location.parent_location_id == location_id,
        Location.campaign_id == campaign_id
    ).count()
    
    if child_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete location that has child locations"
        )
    
    # Check if location has NPCs
    from app.models import NPC
    npc_count = db.query(NPC).filter(
        NPC.location_id == location_id,
        NPC.campaign_id == campaign_id
    ).count()
    
    if npc_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete location that has NPCs assigned to it"
        )
    
    db.delete(location)
    db.commit()
    
    return {"message": "Location deleted successfully"}

@router.get("/templates/fields")
async def get_location_template_fields():
    """Get the field templates for different location types."""
    templates = {
        "region": {
            "name": {"required": True, "type": "text", "label": "Region Name"},
            "description": {"required": False, "type": "textarea", "label": "Description"},
            "history": {"required": False, "type": "textarea", "label": "History"},
            "government_type": {"required": False, "type": "select", "label": "Government Type", "options": [
                "kingdom", "empire", "republic", "city_state", "tribal", "theocracy", "anarchy", "other"
            ]},
            "population": {"required": False, "type": "number", "label": "Total Population"},
            "economic_status": {"required": False, "type": "select", "label": "Economic Status", "options": [
                "prosperous", "stable", "struggling", "impoverished", "wealthy"
            ]},
            "notable_features": {"required": False, "type": "tags", "label": "Notable Features"},
            "climate": {"required": False, "type": "text", "label": "Climate"},
            "natural_resources": {"required": False, "type": "tags", "label": "Natural Resources"}
        },
        "settlement": {
            "name": {"required": True, "type": "text", "label": "Settlement Name"},
            "description": {"required": False, "type": "textarea", "label": "Description"},
            "history": {"required": False, "type": "textarea", "label": "History"},
            "population": {"required": False, "type": "number", "label": "Population"},
            "government_type": {"required": False, "type": "select", "label": "Leadership", "options": [
                "mayor", "council", "lord", "elder", "chieftain", "guild_master", "other"
            ]},
            "economic_status": {"required": False, "type": "select", "label": "Economic Status", "options": [
                "thriving", "prosperous", "stable", "declining", "poor"
            ]},
            "defenses": {"required": False, "type": "textarea", "label": "Defenses"},
            "notable_features": {"required": False, "type": "tags", "label": "Notable Locations"},
            "trade_goods": {"required": False, "type": "tags", "label": "Trade Goods"},
            "demographics": {"required": False, "type": "demographics", "label": "Demographics"}
        },
        "structure": {
            "name": {"required": True, "type": "text", "label": "Building Name"},
            "description": {"required": False, "type": "textarea", "label": "Description"},
            "history": {"required": False, "type": "textarea", "label": "History"},
            "structure_type": {"required": False, "type": "select", "label": "Building Type", "options": [
                "inn", "tavern", "shop", "temple", "guild_hall", "manor", "castle", "tower", "warehouse", "other"
            ]},
            "owner": {"required": False, "type": "text", "label": "Owner/Proprietor"},
            "notable_features": {"required": False, "type": "tags", "label": "Notable Features"},
            "services": {"required": False, "type": "tags", "label": "Services Offered"},
            "security": {"required": False, "type": "text", "label": "Security Measures"},
            "ambient_description": {"required": False, "type": "textarea", "label": "Atmosphere & Ambience"}
        },
        "dungeon": {
            "name": {"required": True, "type": "text", "label": "Dungeon Name"},
            "description": {"required": False, "type": "textarea", "label": "Description"},
            "history": {"required": False, "type": "textarea", "label": "History"},
            "dungeon_type": {"required": False, "type": "select", "label": "Dungeon Type", "options": [
                "ruins", "tomb", "cave", "mine", "fortress", "laboratory", "temple", "prison", "other"
            ]},
            "difficulty": {"required": False, "type": "select", "label": "Difficulty", "options": [
                "easy", "moderate", "hard", "deadly"
            ]},
            "defenses": {"required": False, "type": "textarea", "label": "Traps & Defenses"},
            "notable_features": {"required": False, "type": "tags", "label": "Notable Features"},
            "treasures": {"required": False, "type": "textarea", "label": "Potential Treasures"},
            "ambient_description": {"required": False, "type": "textarea", "label": "Atmosphere"}
        },
        "wilderness": {
            "name": {"required": True, "type": "text", "label": "Area Name"},
            "description": {"required": False, "type": "textarea", "label": "Description"},
            "history": {"required": False, "type": "textarea", "label": "History"},
            "terrain_type": {"required": False, "type": "select", "label": "Terrain Type", "options": [
                "forest", "mountains", "plains", "desert", "swamp", "coast", "river", "lake", "hills", "other"
            ]},
            "climate": {"required": False, "type": "text", "label": "Climate"},
            "dangers": {"required": False, "type": "tags", "label": "Dangers & Hazards"},
            "notable_features": {"required": False, "type": "tags", "label": "Points of Interest"},
            "wildlife": {"required": False, "type": "tags", "label": "Notable Wildlife"},
            "resources": {"required": False, "type": "tags", "label": "Natural Resources"},
            "ambient_description": {"required": False, "type": "textarea", "label": "Atmosphere"}
        }
    }
    
    return templates