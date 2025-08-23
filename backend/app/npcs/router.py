from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import NPC, Campaign, Location, User
from sqlalchemy.orm.attributes import flag_modified
from app.schemas import (
    NPCCreate, NPCUpdate, NPC as NPCSchema, 
    PaginatedNPCResponse
)
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedNPCResponse)
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
    
    # Get the old relationships to determine what changed
    old_relationships = npc.relationships or []
    
    # Update the NPC's relationships
    npc.relationships = relationships
    # Force SQLAlchemy to detect the change to the JSON field
    flag_modified(npc, 'relationships')
    
    # Handle bidirectional relationships
    _update_bidirectional_relationships(db, campaign_id, npc_id, old_relationships, relationships)
    
    db.commit()
    db.refresh(npc)
    
    return {"message": "Relationships updated successfully", "relationships": relationships}

def _update_bidirectional_relationships(db: Session, campaign_id: int, source_npc_id: int, old_relationships: List[dict], new_relationships: List[dict]):
    """Update bidirectional relationships when an NPC's relationships change."""
    
    # Create sets of target IDs for comparison (NPCs and Locations separately)
    old_npc_targets = {rel.get('target_id') for rel in old_relationships if rel.get('target_type') == 'npc' and rel.get('target_id')}
    new_npc_targets = {rel.get('target_id') for rel in new_relationships if rel.get('target_type') == 'npc' and rel.get('target_id')}
    
    old_location_targets = {rel.get('target_id') for rel in old_relationships if rel.get('target_type') == 'location' and rel.get('target_id')}
    new_location_targets = {rel.get('target_id') for rel in new_relationships if rel.get('target_type') == 'location' and rel.get('target_id')}
    
    # Find relationships that were added or removed
    added_npc_targets = new_npc_targets - old_npc_targets
    removed_npc_targets = old_npc_targets - new_npc_targets
    
    added_location_targets = new_location_targets - old_location_targets
    removed_location_targets = old_location_targets - new_location_targets
    
    # Get source NPC info for reciprocal relationships
    source_npc = db.query(NPC).filter(NPC.id == source_npc_id).first()
    
    # Add reciprocal NPC relationships for new connections
    for target_id in added_npc_targets:
        target_npc = db.query(NPC).filter(
            NPC.id == target_id,
            NPC.campaign_id == campaign_id
        ).first()
        
        if target_npc:
            # Find the relationship details from the new relationships
            source_rel = next((rel for rel in new_relationships if rel.get('target_id') == target_id), None)
            if source_rel:
                # Create reciprocal relationship
                target_relationships = target_npc.relationships or []
                
                # Check if reciprocal relationship already exists
                existing_reciprocal = any(
                    rel.get('target_id') == source_npc_id for rel in target_relationships
                )
                
                if not existing_reciprocal:
                    reciprocal_rel = {
                        'target_id': source_npc_id,
                        'target_type': 'npc',
                        'target_name': source_npc.name,
                        'target_occupation': source_npc.occupation,
                        'relationship_type': _get_reciprocal_relationship_type(source_rel.get('relationship_type')),
                        'description': f"Reciprocal relationship with {source_npc.name}",
                        'strength': source_rel.get('strength', 'moderate'),
                        'public_knowledge': source_rel.get('public_knowledge', False)
                    }
                    target_relationships.append(reciprocal_rel)
                    target_npc.relationships = target_relationships
    
    # Add reciprocal Location relationships for new connections
    for target_id in added_location_targets:
        target_location = db.query(Location).filter(
            Location.id == target_id,
            Location.campaign_id == campaign_id
        ).first()
        
        if target_location:
            # Find the relationship details from the new relationships
            source_rel = next((rel for rel in new_relationships if rel.get('target_id') == target_id and rel.get('target_type') == 'location'), None)
            if source_rel:
                # Create reciprocal relationship on location
                target_relationships = target_location.relationships or []
                
                # Check if reciprocal relationship already exists
                existing_reciprocal = any(
                    rel.get('target_id') == source_npc_id and rel.get('target_type') == 'npc' for rel in target_relationships
                )
                
                if not existing_reciprocal:
                    reciprocal_rel = {
                        'target_id': source_npc_id,
                        'target_type': 'npc',
                        'target_name': source_npc.name,
                        'target_occupation': source_npc.occupation,
                        'relationship_type': _get_reciprocal_location_relationship_type(source_rel.get('relationship_type')),
                        'description': f"Connected to {source_npc.name}",
                        'strength': source_rel.get('strength', 'moderate'),
                        'public_knowledge': source_rel.get('public_knowledge', False)
                    }
                    target_relationships.append(reciprocal_rel)
                    target_location.relationships = target_relationships
                    flag_modified(target_location, 'relationships')
    
    # Remove reciprocal NPC relationships for removed connections
    for target_id in removed_npc_targets:
        target_npc = db.query(NPC).filter(
            NPC.id == target_id,
            NPC.campaign_id == campaign_id
        ).first()
        
        if target_npc and target_npc.relationships:
            # Remove reciprocal relationship
            target_relationships = [
                rel for rel in target_npc.relationships 
                if rel.get('target_id') != source_npc_id
            ]
            target_npc.relationships = target_relationships
    
    # Remove reciprocal Location relationships for removed connections
    for target_id in removed_location_targets:
        target_location = db.query(Location).filter(
            Location.id == target_id,
            Location.campaign_id == campaign_id
        ).first()
        
        if target_location and target_location.relationships:
            # Remove reciprocal relationship
            target_relationships = [
                rel for rel in target_location.relationships 
                if not (rel.get('target_id') == source_npc_id and rel.get('target_type') == 'npc')
            ]
            target_location.relationships = target_relationships
            flag_modified(target_location, 'relationships')

def _get_reciprocal_relationship_type(relationship_type: str) -> str:
    """Get the reciprocal relationship type."""
    reciprocal_map = {
        'family': 'family',
        'friend': 'friend',
        'ally': 'ally',
        'romantic': 'romantic',
        'mentor': 'student',
        'student': 'mentor',
        'enemy': 'enemy',
        'rival': 'rival',
        'employer': 'employee',
        'employee': 'employer',
        'neighbor': 'neighbor',
        'acquaintance': 'acquaintance',
        'business_partner': 'business_partner',
        'creditor': 'debtor',
        'debtor': 'creditor',
        'protector': 'protected',
        'protected': 'protector',
        'blackmailer': 'victim',
        'victim': 'blackmailer',
        'other': 'other'
    }
    return reciprocal_map.get(relationship_type, 'other')

def _get_reciprocal_location_relationship_type(relationship_type: str) -> str:
    """Get the reciprocal relationship type for location relationships."""
    reciprocal_map = {
        'lives_in': 'inhabitant',
        'works_at': 'workplace_for',
        'owns': 'owned_by',
        'frequents': 'frequently_visited_by',
        'avoids': 'avoided_by',
        'born_in': 'birthplace_of',
        'exiled_from': 'exiled',
        'wants_to_visit': 'desired_destination_of',
        'has_history_with': 'connected_to',
        'protects': 'protected_by',
        'seeks_to_destroy': 'threatened_by',
        'hiding_in': 'hiding_place_for',
        'imprisoned_in': 'imprisons',
        'rules': 'ruled_by',
        'serves': 'served_by',
        'trades_with': 'trades_with',
        'studies_at': 'place_of_study_for',
        'worships_at': 'place_of_worship_for',
        'performs_at': 'performance_venue_for',
        'other': 'connected_to'
    }
    return reciprocal_map.get(relationship_type, 'connected_to')