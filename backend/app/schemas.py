from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Campaign schemas
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    world_name: Optional[str] = None
    current_date: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    world_name: Optional[str] = None
    current_date: Optional[str] = None

class Campaign(CampaignBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CampaignWithStats(Campaign):
    stats: Dict[str, int]

# NPC schemas
class NPCBase(BaseModel):
    name: str
    race: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    location_id: Optional[int] = None
    personality_traits: Optional[List[str]] = []
    ideals: Optional[str] = None
    bonds: Optional[str] = None
    flaws: Optional[str] = None
    appearance_description: Optional[str] = None
    background: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    relationships: Optional[List[Dict[str, Any]]] = []
    status: str = "draft"
    visibility: str = "dm_only"
    voice_description: Optional[str] = None
    notes: Optional[str] = None

class NPCCreate(NPCBase):
    pass

class NPCUpdate(BaseModel):
    name: Optional[str] = None
    race: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    location_id: Optional[int] = None
    personality_traits: Optional[List[str]] = None
    ideals: Optional[str] = None
    bonds: Optional[str] = None
    flaws: Optional[str] = None
    appearance_description: Optional[str] = None
    background: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    voice_description: Optional[str] = None
    notes: Optional[str] = None

class NPC(NPCBase):
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Location schemas
class LocationBase(BaseModel):
    name: str
    type: Optional[str] = None
    parent_location_id: Optional[int] = None
    population: Optional[int] = None
    demographics: Optional[Dict[str, Any]] = None
    government_type: Optional[str] = None
    economic_status: Optional[str] = None
    notable_features: Optional[List[str]] = []
    description: Optional[str] = None
    history: Optional[str] = None
    current_events: Optional[List[Dict[str, Any]]] = []
    defenses: Optional[str] = None
    trade_goods: Optional[List[Dict[str, Any]]] = []
    connected_locations: Optional[List[Dict[str, Any]]] = []
    status: str = "draft"
    visibility: str = "dm_only"
    ambient_description: Optional[str] = None
    notes: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    parent_location_id: Optional[int] = None
    population: Optional[int] = None
    demographics: Optional[Dict[str, Any]] = None
    government_type: Optional[str] = None
    economic_status: Optional[str] = None
    notable_features: Optional[List[str]] = None
    description: Optional[str] = None
    history: Optional[str] = None
    current_events: Optional[List[Dict[str, Any]]] = None
    defenses: Optional[str] = None
    trade_goods: Optional[List[Dict[str, Any]]] = None
    connected_locations: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    ambient_description: Optional[str] = None
    notes: Optional[str] = None

class Location(LocationBase):
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Organization schemas
class OrganizationBase(BaseModel):
    name: str
    type: Optional[str] = None
    scope: Optional[str] = None
    headquarters_location_id: Optional[int] = None
    leader_npc_id: Optional[int] = None
    goals: Optional[List[str]] = []
    methods: Optional[List[str]] = []
    resources: Optional[str] = None
    influence_level: Optional[str] = None
    membership_size: Optional[str] = None
    notable_members: Optional[List[int]] = []
    allies: Optional[List[int]] = []
    enemies: Optional[List[int]] = []
    reputation: Optional[str] = None
    status: str = "draft"
    visibility: str = "dm_only"
    notes: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Plot Hook schemas
class PlotHookBase(BaseModel):
    title: str
    description: Optional[str] = None
    hook_type: Optional[str] = None
    urgency: Optional[str] = None
    complexity: Optional[str] = None
    related_npcs: Optional[List[int]] = []
    related_locations: Optional[List[int]] = []
    related_organizations: Optional[List[int]] = []
    prerequisites: Optional[List[Dict[str, Any]]] = []
    rewards: Optional[Dict[str, Any]] = None
    consequences: Optional[Dict[str, Any]] = None
    status: str = "draft"
    visibility: str = "dm_only"
    notes: Optional[str] = None

class PlotHookCreate(PlotHookBase):
    pass

class PlotHook(PlotHookBase):
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Event schemas
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: Optional[str] = None
    date: Optional[str] = None
    location_id: Optional[int] = None
    participants: Optional[List[Dict[str, Any]]] = []
    causes: Optional[List[str]] = []
    effects: Optional[List[str]] = []
    visibility: str = "dm_only"
    status: str = "draft"
    notes: Optional[str] = None

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Item schemas
class ItemBase(BaseModel):
    name: str
    type: Optional[str] = None
    rarity: Optional[str] = None
    description: Optional[str] = None
    mechanical_effects: Optional[Dict[str, Any]] = None
    history: Optional[str] = None
    current_owner_id: Optional[int] = None
    current_location_id: Optional[int] = None
    value: Optional[int] = None
    weight: Optional[int] = None
    attunement_required: bool = False
    status: str = "draft"
    visibility: str = "dm_only"
    notes: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Ideas schemas
class IdeaBase(BaseModel):
    content: str
    status: str = "raw_idea"
    idea_type: Optional[str] = None
    priority: str = "medium"
    notes: Optional[str] = None

class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    idea_type: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class Idea(IdeaBase):
    id: int
    campaign_id: int
    ai_session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Pagination
class PaginatedResponse(BaseModel):
    total: int
    items: List[Any]