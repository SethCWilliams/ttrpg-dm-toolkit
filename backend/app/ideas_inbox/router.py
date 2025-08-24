from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Idea, Campaign, User
from app.schemas import IdeaCreate, IdeaUpdate, Idea as IdeaSchema, PaginatedIdeaResponse
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedIdeaResponse)
async def get_ideas(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    idea_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    """Get ideas for a campaign with optional filtering."""
    query = db.query(Idea).filter(Idea.campaign_id == campaign_id)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Idea.content.ilike(search_term) |
            Idea.notes.ilike(search_term)
        )
    
    if status:
        query = query.filter(Idea.status == status)
        
    if idea_type:
        query = query.filter(Idea.idea_type == idea_type)
    
    if priority:
        query = query.filter(Idea.priority == priority)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering (most recent first, then by priority)
    priority_order = {
        'high': 3,
        'medium': 2, 
        'low': 1
    }
    
    ideas = query.order_by(Idea.created_at.desc()).offset(skip).limit(limit).all()
    
    # Sort by priority within each status group
    ideas.sort(key=lambda x: (
        x.status == 'implemented',  # Implemented items last
        -priority_order.get(x.priority, 2),  # High priority first
        -x.id  # Most recent first for ties
    ))
    
    return {
        "total": total,
        "items": ideas
    }

@router.post("/", response_model=IdeaSchema)
async def create_idea(
    campaign_id: int,
    idea_data: IdeaCreate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Create a new idea."""
    db_idea = Idea(
        **idea_data.dict(),
        campaign_id=campaign_id
    )
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    
    return db_idea

@router.get("/{idea_id}", response_model=IdeaSchema)
async def get_idea(
    campaign_id: int,
    idea_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Get a specific idea."""
    idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.campaign_id == campaign_id
    ).first()
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    return idea

@router.put("/{idea_id}", response_model=IdeaSchema)
async def update_idea(
    campaign_id: int,
    idea_id: int,
    idea_data: IdeaUpdate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Update an idea."""
    idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.campaign_id == campaign_id
    ).first()
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Update only provided fields
    update_data = idea_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(idea, field, value)
    
    db.commit()
    db.refresh(idea)
    
    return idea

@router.delete("/{idea_id}")
async def delete_idea(
    campaign_id: int,
    idea_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Delete an idea."""
    idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.campaign_id == campaign_id
    ).first()
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    db.delete(idea)
    db.commit()
    
    return {"message": "Idea deleted successfully"}

@router.post("/{idea_id}/convert")
async def convert_idea_to_element(
    campaign_id: int,
    idea_id: int,
    target_type: str = Query(..., regex="^(npc|location|plot_hook|item|organization|event)$"),
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Convert an idea to a world element (placeholder for future implementation)."""
    idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.campaign_id == campaign_id
    ).first()
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # For now, just mark as implemented
    # Future enhancement: actually create the target element
    idea.status = "implemented"
    idea.notes = f"Converted to {target_type}. {idea.notes or ''}".strip()
    
    db.commit()
    db.refresh(idea)
    
    return {"message": f"Idea marked as converted to {target_type}", "idea": idea}