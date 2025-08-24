from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Event, Campaign, Location, NPC, User
from app.schemas import EventCreate, EventUpdate, Event as EventSchema, PaginatedEventResponse
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedEventResponse)
async def get_events(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None)
):
    """Get events for a campaign with optional filtering."""
    query = db.query(Event).filter(Event.campaign_id == campaign_id)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Event.title.ilike(search_term) |
            Event.description.ilike(search_term) |
            Event.notes.ilike(search_term)
        )
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if status:
        query = query.filter(Event.status == status)
        
    if visibility:
        query = query.filter(Event.visibility == visibility)
    
    if location_id is not None:
        query = query.filter(Event.location_id == location_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    events = query.order_by(Event.date.desc(), Event.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": events
    }

@router.post("/", response_model=EventSchema)
async def create_event(
    campaign_id: int,
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Create a new event."""
    # Validate location if provided
    if event_data.location_id:
        location = db.query(Location).filter(
            Location.id == event_data.location_id,
            Location.campaign_id == campaign_id
        ).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location not found in this campaign"
            )
    
    # Validate participants if provided
    if event_data.participants:
        for participant in event_data.participants:
            if participant.get("type") == "npc" and participant.get("id"):
                npc = db.query(NPC).filter(
                    NPC.id == participant["id"],
                    NPC.campaign_id == campaign_id
                ).first()
                if not npc:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"NPC with id {participant['id']} not found in this campaign"
                    )
    
    db_event = Event(
        **event_data.dict(),
        campaign_id=campaign_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event

@router.get("/{event_id}", response_model=EventSchema)
async def get_event(
    campaign_id: int,
    event_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Get a specific event."""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.campaign_id == campaign_id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event

@router.put("/{event_id}", response_model=EventSchema)
async def update_event(
    campaign_id: int,
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Update an event."""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.campaign_id == campaign_id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Validate location if provided
    if event_data.location_id:
        location = db.query(Location).filter(
            Location.id == event_data.location_id,
            Location.campaign_id == campaign_id
        ).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location not found in this campaign"
            )
    
    # Validate participants if provided
    if event_data.participants:
        for participant in event_data.participants:
            if participant.get("type") == "npc" and participant.get("id"):
                npc = db.query(NPC).filter(
                    NPC.id == participant["id"],
                    NPC.campaign_id == campaign_id
                ).first()
                if not npc:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"NPC with id {participant['id']} not found in this campaign"
                    )
    
    # Update event with new data
    update_data = event_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event

@router.delete("/{event_id}")
async def delete_event(
    campaign_id: int,
    event_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Delete an event."""
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.campaign_id == campaign_id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}