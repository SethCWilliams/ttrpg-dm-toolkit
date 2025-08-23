from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Organization, Campaign, NPC, Location, User
from app.schemas import (
    OrganizationCreate, OrganizationUpdate, Organization as OrganizationSchema,
    PaginatedOrganizationResponse
)
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedOrganizationResponse)
async def get_organizations(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None),
    headquarters_location_id: Optional[int] = Query(None)
):
    """Get organizations for a campaign with optional filtering."""
    query = db.query(Organization).filter(Organization.campaign_id == campaign_id)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Organization.name.ilike(search_term) |
            Organization.reputation.ilike(search_term) |
            Organization.resources.ilike(search_term)
        )
    
    if type:
        query = query.filter(Organization.type == type)
    
    if scope:
        query = query.filter(Organization.scope == scope)
    
    if status:
        query = query.filter(Organization.status == status)
        
    if visibility:
        query = query.filter(Organization.visibility == visibility)
    
    if headquarters_location_id:
        query = query.filter(Organization.headquarters_location_id == headquarters_location_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    organizations = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": organizations
    }

@router.post("/", response_model=OrganizationSchema)
async def create_organization(
    campaign_id: int,
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Create a new organization."""
    # Validate headquarters location if provided
    if org_data.headquarters_location_id:
        location = db.query(Location).filter(
            Location.id == org_data.headquarters_location_id,
            Location.campaign_id == campaign_id
        ).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Headquarters location not found in this campaign"
            )
    
    # Validate leader NPC if provided
    if org_data.leader_npc_id:
        leader = db.query(NPC).filter(
            NPC.id == org_data.leader_npc_id,
            NPC.campaign_id == campaign_id
        ).first()
        if not leader:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leader NPC not found in this campaign"
            )
    
    # Validate notable members if provided
    if org_data.notable_members:
        for member_id in org_data.notable_members:
            member = db.query(NPC).filter(
                NPC.id == member_id,
                NPC.campaign_id == campaign_id
            ).first()
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Member NPC {member_id} not found in this campaign"
                )
    
    db_org = Organization(
        **org_data.dict(),
        campaign_id=campaign_id
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    
    return db_org

@router.get("/{org_id}", response_model=OrganizationSchema)
async def get_organization(
    campaign_id: int,
    org_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Get a specific organization."""
    org = db.query(Organization).filter(
        Organization.id == org_id,
        Organization.campaign_id == campaign_id
    ).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return org

@router.put("/{org_id}", response_model=OrganizationSchema)
async def update_organization(
    campaign_id: int,
    org_id: int,
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Update an organization."""
    org = db.query(Organization).filter(
        Organization.id == org_id,
        Organization.campaign_id == campaign_id
    ).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Validate headquarters location if provided
    if org_data.headquarters_location_id is not None:
        if org_data.headquarters_location_id != org.headquarters_location_id:
            location = db.query(Location).filter(
                Location.id == org_data.headquarters_location_id,
                Location.campaign_id == campaign_id
            ).first()
            if not location:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Headquarters location not found in this campaign"
                )
    
    # Validate leader NPC if provided
    if org_data.leader_npc_id is not None:
        if org_data.leader_npc_id != org.leader_npc_id:
            leader = db.query(NPC).filter(
                NPC.id == org_data.leader_npc_id,
                NPC.campaign_id == campaign_id
            ).first()
            if not leader:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Leader NPC not found in this campaign"
                )
    
    # Update only provided fields
    update_data = org_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    db.commit()
    db.refresh(org)
    
    return org

@router.delete("/{org_id}")
async def delete_organization(
    campaign_id: int,
    org_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Delete an organization."""
    org = db.query(Organization).filter(
        Organization.id == org_id,
        Organization.campaign_id == campaign_id
    ).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    db.delete(org)
    db.commit()
    
    return {"message": "Organization deleted successfully"}

@router.get("/templates/fields")
async def get_organization_template_fields():
    """Get template fields for different organization types."""
    templates = {
        "guild": {
            "membership_requirements": {"required": False, "type": "textarea", "label": "Membership Requirements"},
            "services_offered": {"required": False, "type": "tags", "label": "Services Offered"},
            "guild_hall_features": {"required": False, "type": "tags", "label": "Guild Hall Features"},
            "ranks": {"required": False, "type": "tags", "label": "Organizational Ranks"}
        },
        "government": {
            "political_structure": {"required": False, "type": "select", "label": "Political Structure",
                                  "options": ["monarchy", "democracy", "oligarchy", "theocracy", "council", "other"]},
            "jurisdiction": {"required": False, "type": "text", "label": "Jurisdiction Area"},
            "laws": {"required": False, "type": "textarea", "label": "Key Laws & Policies"},
            "government_branches": {"required": False, "type": "tags", "label": "Government Branches"}
        },
        "religion": {
            "deity": {"required": False, "type": "text", "label": "Deity/Pantheon"},
            "core_beliefs": {"required": False, "type": "textarea", "label": "Core Beliefs"},
            "holy_symbol": {"required": False, "type": "text", "label": "Holy Symbol"},
            "religious_holidays": {"required": False, "type": "tags", "label": "Religious Holidays"},
            "temples": {"required": False, "type": "tags", "label": "Temples & Shrines"}
        },
        "criminal": {
            "criminal_activities": {"required": False, "type": "tags", "label": "Criminal Activities"},
            "territory": {"required": False, "type": "text", "label": "Controlled Territory"},
            "law_enforcement_relations": {"required": False, "type": "textarea", "label": "Law Enforcement Relations"},
            "criminal_code": {"required": False, "type": "textarea", "label": "Internal Code of Conduct"}
        },
        "military": {
            "military_branch": {"required": False, "type": "select", "label": "Military Branch",
                               "options": ["army", "navy", "air_force", "marines", "special_forces", "militia", "mercenary"]},
            "equipment": {"required": False, "type": "tags", "label": "Standard Equipment"},
            "training_facilities": {"required": False, "type": "tags", "label": "Training Facilities"},
            "chain_of_command": {"required": False, "type": "tags", "label": "Chain of Command"}
        },
        "academic": {
            "fields_of_study": {"required": False, "type": "tags", "label": "Fields of Study"},
            "research_projects": {"required": False, "type": "tags", "label": "Current Research"},
            "library_resources": {"required": False, "type": "textarea", "label": "Library & Resources"},
            "academic_ranks": {"required": False, "type": "tags", "label": "Academic Ranks"}
        },
        "merchant": {
            "trade_goods": {"required": False, "type": "tags", "label": "Primary Trade Goods"},
            "trade_routes": {"required": False, "type": "tags", "label": "Trade Routes"},
            "business_practices": {"required": False, "type": "textarea", "label": "Business Practices"},
            "merchant_connections": {"required": False, "type": "tags", "label": "Merchant Connections"}
        }
    }
    return templates