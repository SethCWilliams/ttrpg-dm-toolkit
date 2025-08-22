from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import NPC, Campaign, Location, User
from app.schemas import (
    NPCCreate, NPCUpdate, NPC as NPCSchema, 
    PaginatedResponse
)
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_npcs(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None)
):
    """Get NPCs for a campaign with optional filtering."""
    query = db.query(NPC).filter(NPC.campaign_id == campaign_id)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            NPC.name.ilike(search_term) |
            NPC.occupation.ilike(search_term) |
            NPC.background.ilike(search_term)
        )
    
    if location_id:
        query = query.filter(NPC.location_id == location_id)
    
    if status:
        query = query.filter(NPC.status == status)
        
    if visibility:
        query = query.filter(NPC.visibility == visibility)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    npcs = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": npcs
    }

@router.post("/", response_model=NPCSchema)
async def create_npc(
    campaign_id: int,
    npc_data: NPCCreate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Create a new NPC."""
    # Validate location if provided
    if npc_data.location_id:
        location = db.query(Location).filter(
            Location.id == npc_data.location_id,
            Location.campaign_id == campaign_id
        ).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location not found in this campaign"
            )
    
    db_npc = NPC(
        **npc_data.dict(),
        campaign_id=campaign_id
    )
    db.add(db_npc)
    db.commit()
    db.refresh(db_npc)
    
    return db_npc

@router.get("/{npc_id}", response_model=NPCSchema)
async def get_npc(
    campaign_id: int,
    npc_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Get a specific NPC."""
    npc = db.query(NPC).filter(
        NPC.id == npc_id,
        NPC.campaign_id == campaign_id
    ).first()
    
    if not npc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NPC not found"
        )
    
    return npc

@router.put("/{npc_id}", response_model=NPCSchema)
async def update_npc(
    campaign_id: int,
    npc_id: int,
    npc_data: NPCUpdate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Update an NPC."""
    npc = db.query(NPC).filter(
        NPC.id == npc_id,
        NPC.campaign_id == campaign_id
    ).first()
    
    if not npc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NPC not found"
        )
    
    # Validate location if provided
    if npc_data.location_id is not None:
        if npc_data.location_id != npc.location_id:  # Only check if changed
            location = db.query(Location).filter(
                Location.id == npc_data.location_id,
                Location.campaign_id == campaign_id
            ).first()
            if not location:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Location not found in this campaign"
                )
    
    # Update only provided fields
    update_data = npc_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(npc, field, value)
    
    db.commit()
    db.refresh(npc)
    
    return npc

@router.delete("/{npc_id}")
async def delete_npc(
    campaign_id: int,
    npc_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Delete an NPC."""
    npc = db.query(NPC).filter(
        NPC.id == npc_id,
        NPC.campaign_id == campaign_id
    ).first()
    
    if not npc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NPC not found"
        )
    
    db.delete(npc)
    db.commit()
    
    return {"message": "NPC deleted successfully"}

@router.get("/{npc_id}/relationships")
async def get_npc_relationships(
    campaign_id: int,
    npc_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Get relationships for a specific NPC."""
    npc = db.query(NPC).filter(
        NPC.id == npc_id,
        NPC.campaign_id == campaign_id
    ).first()
    
    if not npc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NPC not found"
        )
    
    relationships = npc.relationships or []
    
    # Enrich relationships with target NPC details
    enriched_relationships = []
    for rel in relationships:
        if rel.get('target_type') == 'npc':
            target_npc = db.query(NPC).filter(
                NPC.id == rel.get('target_id'),
                NPC.campaign_id == campaign_id
            ).first()
            if target_npc:
                enriched_rel = {
                    **rel,
                    'target_name': target_npc.name,
                    'target_occupation': target_npc.occupation
                }
                enriched_relationships.append(enriched_rel)
        else:
            enriched_relationships.append(rel)
    
    return {
        "npc_id": npc_id,
        "npc_name": npc.name,
        "relationships": enriched_relationships
    }

@router.put("/{npc_id}/relationships")
async def update_npc_relationships(
    campaign_id: int,
    npc_id: int,
    relationships: List[dict],
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Update relationships for an NPC."""
    npc = db.query(NPC).filter(
        NPC.id == npc_id,
        NPC.campaign_id == campaign_id
    ).first()
    
    if not npc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NPC not found"
        )
    
    # Validate relationship targets exist in the campaign
    for rel in relationships:
        if rel.get('target_type') == 'npc':
            target_npc = db.query(NPC).filter(
                NPC.id == rel.get('target_id'),
                NPC.campaign_id == campaign_id
            ).first()
            if not target_npc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Target NPC {rel.get('target_id')} not found in this campaign"
                )
    
    npc.relationships = relationships
    db.commit()
    db.refresh(npc)
    
    return {"message": "Relationships updated successfully", "relationships": relationships}