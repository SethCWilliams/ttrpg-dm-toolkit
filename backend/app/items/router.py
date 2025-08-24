from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Item, Campaign, NPC, Location, User
from app.schemas import ItemCreate, ItemUpdate, Item as ItemSchema, PaginatedItemResponse
from app.auth.router import get_current_user
from app.campaigns.router import verify_campaign_access

router = APIRouter()

@router.get("/", response_model=PaginatedItemResponse)
async def get_items(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    rarity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None),
    current_owner_id: Optional[int] = Query(None),
    current_location_id: Optional[int] = Query(None),
    attunement_required: Optional[bool] = Query(None)
):
    """Get items for a campaign with optional filtering."""
    query = db.query(Item).filter(Item.campaign_id == campaign_id)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Item.name.ilike(search_term) |
            Item.description.ilike(search_term) |
            Item.history.ilike(search_term) |
            Item.notes.ilike(search_term)
        )
    
    if type:
        query = query.filter(Item.type == type)
    
    if rarity:
        query = query.filter(Item.rarity == rarity)
    
    if status:
        query = query.filter(Item.status == status)
        
    if visibility:
        query = query.filter(Item.visibility == visibility)
    
    if current_owner_id is not None:
        query = query.filter(Item.current_owner_id == current_owner_id)
    
    if current_location_id is not None:
        query = query.filter(Item.current_location_id == current_location_id)
    
    if attunement_required is not None:
        query = query.filter(Item.attunement_required == attunement_required)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    items = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": items
    }

@router.post("/", response_model=ItemSchema)
async def create_item(
    campaign_id: int,
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Create a new item."""
    # Validate current owner NPC if provided
    if item_data.current_owner_id:
        owner = db.query(NPC).filter(
            NPC.id == item_data.current_owner_id,
            NPC.campaign_id == campaign_id
        ).first()
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner NPC not found in this campaign"
            )
    
    # Validate current location if provided
    if item_data.current_location_id:
        location = db.query(Location).filter(
            Location.id == item_data.current_location_id,
            Location.campaign_id == campaign_id
        ).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location not found in this campaign"
            )
    
    db_item = Item(
        **item_data.dict(),
        campaign_id=campaign_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.get("/{item_id}", response_model=ItemSchema)
async def get_item(
    campaign_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Get a specific item."""
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.campaign_id == campaign_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item

@router.put("/{item_id}", response_model=ItemSchema)
async def update_item(
    campaign_id: int,
    item_id: int,
    item_data: ItemUpdate,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Update an item."""
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.campaign_id == campaign_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Validate current owner NPC if provided
    if item_data.current_owner_id:
        owner = db.query(NPC).filter(
            NPC.id == item_data.current_owner_id,
            NPC.campaign_id == campaign_id
        ).first()
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner NPC not found in this campaign"
            )
    
    # Validate current location if provided
    if item_data.current_location_id:
        location = db.query(Location).filter(
            Location.id == item_data.current_location_id,
            Location.campaign_id == campaign_id
        ).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location not found in this campaign"
            )
    
    # Update only provided fields
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item

@router.delete("/{item_id}")
async def delete_item(
    campaign_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    campaign: Campaign = Depends(verify_campaign_access),
    db: Session = Depends(get_db)
):
    """Delete an item."""
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.campaign_id == campaign_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item deleted successfully"}

@router.get("/templates/fields")
async def get_item_template_fields():
    """Get template fields for different item types."""
    templates = {
        "weapon": {
            "damage": {"required": False, "type": "text", "label": "Damage"},
            "damage_type": {"required": False, "type": "select", "label": "Damage Type",
                           "options": ["slashing", "piercing", "bludgeoning", "fire", "cold", "lightning", "thunder", "poison", "acid", "psychic", "radiant", "necrotic", "force"]},
            "weapon_category": {"required": False, "type": "select", "label": "Weapon Category",
                              "options": ["simple_melee", "martial_melee", "simple_ranged", "martial_ranged"]},
            "properties": {"required": False, "type": "tags", "label": "Weapon Properties"},
            "range": {"required": False, "type": "text", "label": "Range"}
        },
        "armor": {
            "armor_class": {"required": False, "type": "text", "label": "Armor Class"},
            "armor_type": {"required": False, "type": "select", "label": "Armor Type",
                          "options": ["light", "medium", "heavy", "shield"]},
            "stealth_disadvantage": {"required": False, "type": "select", "label": "Stealth Disadvantage",
                                   "options": ["yes", "no"]},
            "strength_requirement": {"required": False, "type": "text", "label": "Strength Requirement"}
        },
        "tool": {
            "tool_type": {"required": False, "type": "select", "label": "Tool Type",
                         "options": ["artisan", "gaming", "musical", "other"]},
            "proficiency_bonus": {"required": False, "type": "text", "label": "Proficiency Bonus"},
            "special_uses": {"required": False, "type": "tags", "label": "Special Uses"}
        },
        "treasure": {
            "art_object": {"required": False, "type": "select", "label": "Art Object",
                          "options": ["yes", "no"]},
            "gemstone": {"required": False, "type": "select", "label": "Gemstone",
                        "options": ["yes", "no"]},
            "trade_goods": {"required": False, "type": "select", "label": "Trade Goods",
                           "options": ["yes", "no"]},
            "coin_type": {"required": False, "type": "select", "label": "Coin Type",
                         "options": ["copper", "silver", "electrum", "gold", "platinum"]}
        },
        "consumable": {
            "consumable_type": {"required": False, "type": "select", "label": "Consumable Type",
                               "options": ["potion", "scroll", "food", "ammunition", "other"]},
            "uses": {"required": False, "type": "text", "label": "Number of Uses"},
            "duration": {"required": False, "type": "text", "label": "Effect Duration"},
            "save_dc": {"required": False, "type": "text", "label": "Save DC"}
        },
        "quest_item": {
            "quest_importance": {"required": False, "type": "select", "label": "Quest Importance",
                               "options": ["minor", "major", "critical"]},
            "plot_significance": {"required": False, "type": "textarea", "label": "Plot Significance"},
            "activation_method": {"required": False, "type": "textarea", "label": "Activation Method"}
        },
        "artifact": {
            "artifact_type": {"required": False, "type": "select", "label": "Artifact Type",
                             "options": ["major", "minor", "sentient"]},
            "creator": {"required": False, "type": "text", "label": "Creator"},
            "age": {"required": False, "type": "text", "label": "Age"},
            "powers": {"required": False, "type": "tags", "label": "Artifact Powers"},
            "curses": {"required": False, "type": "tags", "label": "Artifact Curses"},
            "sentience": {"required": False, "type": "textarea", "label": "Sentience Details"}
        }
    }
    return templates