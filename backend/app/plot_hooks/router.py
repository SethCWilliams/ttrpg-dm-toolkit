from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import PlotHook, Campaign, NPC, Location, Organization, User
from app.schemas import (
    PlotHookCreate, PlotHookUpdate, PlotHook as PlotHookSchema,
    PaginatedPlotHookResponse
)
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedPlotHookResponse)
async def get_plot_hooks(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    hook_type: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    complexity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None)
):
    """Get plot hooks for a campaign with optional filtering."""
    query = db.query(PlotHook).filter(PlotHook.campaign_id == campaign_id)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            PlotHook.title.ilike(search_term) |
            PlotHook.description.ilike(search_term) |
            PlotHook.notes.ilike(search_term)
        )
    
    if hook_type:
        query = query.filter(PlotHook.hook_type == hook_type)
    
    if urgency:
        query = query.filter(PlotHook.urgency == urgency)
    
    if complexity:
        query = query.filter(PlotHook.complexity == complexity)
    
    if status:
        query = query.filter(PlotHook.status == status)
        
    if visibility:
        query = query.filter(PlotHook.visibility == visibility)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    plot_hooks = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": plot_hooks
    }

@router.post("/", response_model=PlotHookSchema)
async def create_plot_hook(
    campaign_id: int,
    hook_data: PlotHookCreate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Create a new plot hook."""
    # Validate related NPCs if provided
    if hook_data.related_npcs:
        for npc_id in hook_data.related_npcs:
            npc = db.query(NPC).filter(
                NPC.id == npc_id,
                NPC.campaign_id == campaign_id
            ).first()
            if not npc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Related NPC {npc_id} not found in this campaign"
                )
    
    # Validate related locations if provided
    if hook_data.related_locations:
        for location_id in hook_data.related_locations:
            location = db.query(Location).filter(
                Location.id == location_id,
                Location.campaign_id == campaign_id
            ).first()
            if not location:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Related location {location_id} not found in this campaign"
                )
    
    # Validate related organizations if provided
    if hook_data.related_organizations:
        for org_id in hook_data.related_organizations:
            organization = db.query(Organization).filter(
                Organization.id == org_id,
                Organization.campaign_id == campaign_id
            ).first()
            if not organization:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Related organization {org_id} not found in this campaign"
                )
    
    db_hook = PlotHook(
        **hook_data.dict(),
        campaign_id=campaign_id
    )
    db.add(db_hook)
    db.commit()
    db.refresh(db_hook)
    
    return db_hook

@router.get("/{hook_id}", response_model=PlotHookSchema)
async def get_plot_hook(
    campaign_id: int,
    hook_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Get a specific plot hook."""
    hook = db.query(PlotHook).filter(
        PlotHook.id == hook_id,
        PlotHook.campaign_id == campaign_id
    ).first()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot hook not found"
        )
    
    return hook

@router.put("/{hook_id}", response_model=PlotHookSchema)
async def update_plot_hook(
    campaign_id: int,
    hook_id: int,
    hook_data: PlotHookUpdate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Update a plot hook."""
    hook = db.query(PlotHook).filter(
        PlotHook.id == hook_id,
        PlotHook.campaign_id == campaign_id
    ).first()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot hook not found"
        )
    
    # Validate related entities similar to create
    if hook_data.related_npcs:
        for npc_id in hook_data.related_npcs:
            npc = db.query(NPC).filter(
                NPC.id == npc_id,
                NPC.campaign_id == campaign_id
            ).first()
            if not npc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Related NPC {npc_id} not found in this campaign"
                )
    
    if hook_data.related_locations:
        for location_id in hook_data.related_locations:
            location = db.query(Location).filter(
                Location.id == location_id,
                Location.campaign_id == campaign_id
            ).first()
            if not location:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Related location {location_id} not found in this campaign"
                )
    
    if hook_data.related_organizations:
        for org_id in hook_data.related_organizations:
            organization = db.query(Organization).filter(
                Organization.id == org_id,
                Organization.campaign_id == campaign_id
            ).first()
            if not organization:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Related organization {org_id} not found in this campaign"
                )
    
    # Update only provided fields
    update_data = hook_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hook, field, value)
    
    db.commit()
    db.refresh(hook)
    
    return hook

@router.delete("/{hook_id}")
async def delete_plot_hook(
    campaign_id: int,
    hook_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Delete a plot hook."""
    hook = db.query(PlotHook).filter(
        PlotHook.id == hook_id,
        PlotHook.campaign_id == campaign_id
    ).first()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot hook not found"
        )
    
    db.delete(hook)
    db.commit()
    
    return {"message": "Plot hook deleted successfully"}

@router.get("/templates/fields")
async def get_plot_hook_template_fields():
    """Get template fields for different plot hook types."""
    templates = {
        "main_quest": {
            "chapter": {"required": False, "type": "text", "label": "Chapter/Arc"},
            "main_objective": {"required": True, "type": "textarea", "label": "Main Objective"},
            "key_moments": {"required": False, "type": "tags", "label": "Key Story Moments"}
        },
        "side_quest": {
            "quest_giver": {"required": False, "type": "text", "label": "Quest Giver"},
            "time_limit": {"required": False, "type": "text", "label": "Time Limit"},
            "optional_objectives": {"required": False, "type": "tags", "label": "Optional Objectives"}
        },
        "personal": {
            "character_focus": {"required": False, "type": "text", "label": "Character Focus"},
            "backstory_connection": {"required": False, "type": "textarea", "label": "Backstory Connection"},
            "character_growth": {"required": False, "type": "textarea", "label": "Character Growth Opportunity"}
        },
        "political": {
            "factions_involved": {"required": False, "type": "tags", "label": "Factions Involved"},
            "political_stakes": {"required": False, "type": "textarea", "label": "Political Stakes"},
            "diplomatic_options": {"required": False, "type": "tags", "label": "Diplomatic Solutions"}
        },
        "mystery": {
            "clues": {"required": False, "type": "tags", "label": "Key Clues"},
            "red_herrings": {"required": False, "type": "tags", "label": "Red Herrings"},
            "revelation": {"required": False, "type": "textarea", "label": "Final Revelation"}
        },
        "combat": {
            "enemy_types": {"required": False, "type": "tags", "label": "Enemy Types"},
            "battle_conditions": {"required": False, "type": "textarea", "label": "Special Battle Conditions"},
            "tactical_considerations": {"required": False, "type": "tags", "label": "Tactical Elements"}
        },
        "social": {
            "social_challenges": {"required": False, "type": "tags", "label": "Social Challenges"},
            "key_npcs": {"required": False, "type": "tags", "label": "Key NPCs Involved"},
            "social_stakes": {"required": False, "type": "textarea", "label": "Social Stakes"}
        }
    }
    return templates