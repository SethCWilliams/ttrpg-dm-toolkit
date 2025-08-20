from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Campaign, User, NPC, Location, Organization, PlotHook, Event, Item
from app.schemas import (
    CampaignCreate, CampaignUpdate, Campaign as CampaignSchema, 
    CampaignWithStats
)
from app.auth.router import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CampaignSchema])
async def get_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaigns = db.query(Campaign).filter(Campaign.user_id == current_user.id).all()
    return campaigns

@router.post("/", response_model=CampaignSchema)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_campaign = Campaign(
        **campaign_data.dict(),
        user_id=current_user.id
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.get("/{campaign_id}", response_model=CampaignWithStats)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Calculate stats
    stats = {
        "npc_count": db.query(NPC).filter(NPC.campaign_id == campaign_id).count(),
        "location_count": db.query(Location).filter(Location.campaign_id == campaign_id).count(),
        "organization_count": db.query(Organization).filter(Organization.campaign_id == campaign_id).count(),
        "plot_hook_count": db.query(PlotHook).filter(PlotHook.campaign_id == campaign_id).count(),
        "event_count": db.query(Event).filter(Event.campaign_id == campaign_id).count(),
        "item_count": db.query(Item).filter(Item.campaign_id == campaign_id).count(),
    }
    
    # Convert to dict and add stats
    campaign_dict = {
        **campaign.__dict__,
        "stats": stats
    }
    
    return campaign_dict

@router.put("/{campaign_id}", response_model=CampaignSchema)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update only provided fields
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    return campaign

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    db.delete(campaign)
    db.commit()
    return {"message": "Campaign deleted successfully"}

# Helper function to verify campaign ownership
async def verify_campaign_access(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Campaign:
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign