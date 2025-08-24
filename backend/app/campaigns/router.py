from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models import Campaign, User, NPC, Location, Organization, PlotHook, Event, Item, SessionNote, Idea
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
        "session_note_count": db.query(SessionNote).filter(SessionNote.campaign_id == campaign_id).count(),
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

@router.get("/{campaign_id}/search")
async def global_search(
    campaign_id: int,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results per category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Global search across all campaign content"""
    # Verify campaign access
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    search_filter = f"%{q}%"
    results = {}
    
    # Search NPCs
    npc_results = db.query(NPC).filter(
        NPC.campaign_id == campaign_id,
        or_(
            NPC.name.ilike(search_filter),
            NPC.occupation.ilike(search_filter),
            NPC.background.ilike(search_filter),
            NPC.notes.ilike(search_filter)
        )
    ).limit(limit).all()
    
    results['npcs'] = [
        {
            'id': npc.id,
            'name': npc.name,
            'type': 'npc',
            'description': npc.occupation or 'NPC',
            'url': f'/campaigns/{campaign_id}/npcs/{npc.id}',
            'match_field': 'name' if q.lower() in (npc.name or '').lower() else 'occupation'
        }
        for npc in npc_results
    ]
    
    # Search Locations
    location_results = db.query(Location).filter(
        Location.campaign_id == campaign_id,
        or_(
            Location.name.ilike(search_filter),
            Location.description.ilike(search_filter),
            Location.notes.ilike(search_filter)
        )
    ).limit(limit).all()
    
    results['locations'] = [
        {
            'id': loc.id,
            'name': loc.name,
            'type': 'location',
            'description': (loc.type or 'Location').replace('_', ' ').title(),
            'url': f'/campaigns/{campaign_id}/locations/{loc.id}',
            'match_field': 'name' if q.lower() in (loc.name or '').lower() else 'description'
        }
        for loc in location_results
    ]
    
    # Search Organizations
    org_results = db.query(Organization).filter(
        Organization.campaign_id == campaign_id,
        or_(
            Organization.name.ilike(search_filter),
            Organization.resources.ilike(search_filter),
            Organization.reputation.ilike(search_filter),
            Organization.notes.ilike(search_filter)
        )
    ).limit(limit).all()
    
    results['organizations'] = [
        {
            'id': org.id,
            'name': org.name,
            'type': 'organization',
            'description': (org.type or 'Organization').replace('_', ' ').title(),
            'url': f'/campaigns/{campaign_id}/organizations/{org.id}',
            'match_field': 'name' if q.lower() in (org.name or '').lower() else 'type'
        }
        for org in org_results
    ]
    
    # Search Plot Hooks
    plot_results = db.query(PlotHook).filter(
        PlotHook.campaign_id == campaign_id,
        or_(
            PlotHook.title.ilike(search_filter),
            PlotHook.description.ilike(search_filter),
            PlotHook.notes.ilike(search_filter)
        )
    ).limit(limit).all()
    
    results['plot_hooks'] = [
        {
            'id': hook.id,
            'name': hook.title,
            'type': 'plot_hook',
            'description': f"Plot Hook - {hook.status or 'Draft'}".title(),
            'url': f'/campaigns/{campaign_id}/plot-hooks/{hook.id}',
            'match_field': 'title' if q.lower() in (hook.title or '').lower() else 'description'
        }
        for hook in plot_results
    ]
    
    # Search Items
    item_results = db.query(Item).filter(
        Item.campaign_id == campaign_id,
        or_(
            Item.name.ilike(search_filter),
            Item.description.ilike(search_filter),
            Item.notes.ilike(search_filter)
        )
    ).limit(limit).all()
    
    results['items'] = [
        {
            'id': item.id,
            'name': item.name,
            'type': 'item',
            'description': f"{(item.item_type or 'Item').replace('_', ' ').title()} - {item.rarity or 'Common'}".title(),
            'url': f'/campaigns/{campaign_id}/items/{item.id}',
            'match_field': 'name' if q.lower() in (item.name or '').lower() else 'description'
        }
        for item in item_results
    ]
    
    # Search Events
    event_results = db.query(Event).filter(
        Event.campaign_id == campaign_id,
        or_(
            Event.title.ilike(search_filter),
            Event.description.ilike(search_filter),
            Event.notes.ilike(search_filter)
        )
    ).limit(limit).all()
    
    results['events'] = [
        {
            'id': event.id,
            'name': event.title,
            'type': 'event',
            'description': f"Event - {(event.event_type or 'Event').replace('_', ' ').title()}",
            'url': f'/campaigns/{campaign_id}/events/{event.id}',
            'match_field': 'title' if q.lower() in (event.title or '').lower() else 'description'
        }
        for event in event_results
    ]
    
    # Search Ideas
    idea_results = db.query(Idea).filter(
        Idea.campaign_id == campaign_id,
        or_(
            Idea.content.ilike(search_filter),
            Idea.notes.ilike(search_filter)
        )
    ).limit(limit).all()
    
    results['ideas'] = [
        {
            'id': idea.id,
            'name': idea.content[:50] + ('...' if len(idea.content) > 50 else ''),
            'type': 'idea',
            'description': f"Idea - {(idea.status or 'Raw Idea').replace('_', ' ').title()}",
            'url': f'/campaigns/{campaign_id}/ideas/{idea.id}',
            'match_field': 'content'
        }
        for idea in idea_results
    ]
    
    # Search Session Notes
    session_results = db.query(SessionNote).filter(
        SessionNote.campaign_id == campaign_id,
        or_(
            SessionNote.title.ilike(search_filter),
            SessionNote.summary.ilike(search_filter),
            SessionNote.detailed_notes.ilike(search_filter),
            SessionNote.dm_notes.ilike(search_filter)
        )
    ).limit(limit).all()
    
    results['sessions'] = [
        {
            'id': session.id,
            'name': session.title,
            'type': 'session',
            'description': f"Session {session.session_number or 'Note'} - {(session.status or 'Draft').title()}",
            'url': f'/campaigns/{campaign_id}/sessions/{session.id}',
            'match_field': 'title' if q.lower() in (session.title or '').lower() else 'summary'
        }
        for session in session_results
    ]
    
    # Calculate total results
    total_results = sum(len(results[category]) for category in results.keys())
    
    return {
        'query': q,
        'total_results': total_results,
        'results': results
    }

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