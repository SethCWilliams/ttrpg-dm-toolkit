from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import SessionNote, Campaign, User
from app.schemas import (
    SessionNoteCreate, SessionNoteUpdate, SessionNote as SessionNoteSchema,
    PaginatedSessionNoteResponse
)
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedSessionNoteResponse)
async def get_session_notes(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None),
    session_number: Optional[int] = Query(None)
):
    query = db.query(SessionNote).filter(SessionNote.campaign_id == campaign_id)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (SessionNote.title.ilike(search_filter)) |
            (SessionNote.summary.ilike(search_filter)) |
            (SessionNote.detailed_notes.ilike(search_filter))
        )
    
    if status:
        query = query.filter(SessionNote.status == status)
    
    if visibility:
        query = query.filter(SessionNote.visibility == visibility)
    
    if session_number is not None:
        query = query.filter(SessionNote.session_number == session_number)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination and ordering
    session_notes = query.order_by(SessionNote.session_number.desc().nullslast(), SessionNote.created_at.desc()).offset(skip).limit(limit).all()
    
    return PaginatedSessionNoteResponse(total=total, items=session_notes)

@router.get("/{session_note_id}", response_model=SessionNoteSchema)
async def get_session_note(
    campaign_id: int,
    session_note_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    session_note = db.query(SessionNote).filter(
        SessionNote.id == session_note_id,
        SessionNote.campaign_id == campaign_id
    ).first()
    
    if not session_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )
    
    return session_note

@router.post("/", response_model=SessionNoteSchema)
async def create_session_note(
    campaign_id: int,
    session_note_data: SessionNoteCreate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    # Auto-generate session number if not provided
    session_number = session_note_data.session_number
    if session_number is None:
        last_session = db.query(SessionNote).filter(
            SessionNote.campaign_id == campaign_id,
            SessionNote.session_number.isnot(None)
        ).order_by(SessionNote.session_number.desc()).first()
        
        session_number = (last_session.session_number + 1) if last_session else 1
    
    # Create new session note
    db_session_note = SessionNote(
        campaign_id=campaign_id,
        session_number=session_number,
        **session_note_data.dict(exclude={"session_number"})
    )
    
    db.add(db_session_note)
    db.commit()
    db.refresh(db_session_note)
    
    return db_session_note

@router.put("/{session_note_id}", response_model=SessionNoteSchema)
async def update_session_note(
    campaign_id: int,
    session_note_id: int,
    session_note_data: SessionNoteUpdate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    session_note = db.query(SessionNote).filter(
        SessionNote.id == session_note_id,
        SessionNote.campaign_id == campaign_id
    ).first()
    
    if not session_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )
    
    # Update only provided fields
    update_data = session_note_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session_note, field, value)
    
    db.commit()
    db.refresh(session_note)
    return session_note

@router.delete("/{session_note_id}")
async def delete_session_note(
    campaign_id: int,
    session_note_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    session_note = db.query(SessionNote).filter(
        SessionNote.id == session_note_id,
        SessionNote.campaign_id == campaign_id
    ).first()
    
    if not session_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )
    
    db.delete(session_note)
    db.commit()
    return {"message": "Session note deleted successfully"}

@router.post("/{session_note_id}/duplicate", response_model=SessionNoteSchema)
async def duplicate_session_note(
    campaign_id: int,
    session_note_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Duplicate a session note as a template for the next session"""
    original_note = db.query(SessionNote).filter(
        SessionNote.id == session_note_id,
        SessionNote.campaign_id == campaign_id
    ).first()
    
    if not original_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )
    
    # Get next session number
    last_session = db.query(SessionNote).filter(
        SessionNote.campaign_id == campaign_id,
        SessionNote.session_number.isnot(None)
    ).order_by(SessionNote.session_number.desc()).first()
    
    next_session_number = (last_session.session_number + 1) if last_session else 1
    
    # Create duplicate with reset fields
    duplicate_note = SessionNote(
        campaign_id=campaign_id,
        title=f"Session {next_session_number}",
        session_number=next_session_number,
        session_date="",
        in_world_date=original_note.in_world_date,
        summary="",
        detailed_notes="",
        player_characters=original_note.player_characters or [],
        npcs_encountered=[],
        locations_visited=[],
        plot_hooks_advanced=[],
        events_occurred=[],
        items_acquired=[],
        experience_gained=0,
        loot_acquired=[],
        combat_encounters=[],
        social_encounters=[],
        exploration_discoveries=[],
        world_state_changes=[],
        dm_notes=original_note.next_session_prep or "",
        next_session_prep="",
        status="draft",
        visibility=original_note.visibility
    )
    
    db.add(duplicate_note)
    db.commit()
    db.refresh(duplicate_note)
    
    return duplicate_note