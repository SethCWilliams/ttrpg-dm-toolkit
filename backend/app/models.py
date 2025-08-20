from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    world_name = Column(String(200))
    current_date = Column(String(100))  # In-world calendar date
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    npcs = relationship("NPC", back_populates="campaign", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="campaign", cascade="all, delete-orphan")
    organizations = relationship("Organization", back_populates="campaign", cascade="all, delete-orphan")
    plot_hooks = relationship("PlotHook", back_populates="campaign", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="campaign", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="campaign", cascade="all, delete-orphan")
    ideas_inbox = relationship("Idea", back_populates="campaign", cascade="all, delete-orphan")

class NPC(Base):
    __tablename__ = "npcs"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(200), nullable=False, index=True)
    race = Column(String(100))
    gender = Column(String(50))
    age = Column(Integer)
    occupation = Column(String(200))
    location_id = Column(Integer, ForeignKey("locations.id"))
    personality_traits = Column(JSON)  # Array of strings
    ideals = Column(Text)
    bonds = Column(Text)
    flaws = Column(Text)
    appearance_description = Column(Text)
    background = Column(Text)
    stats = Column(JSON)  # Game statistics object
    relationships = Column(JSON)  # Array of relationship objects
    status = Column(String(50), default="draft")  # draft, active, historical, dead
    visibility = Column(String(50), default="dm_only")  # dm_only, player_known, partially_known
    image_path = Column(String(500))
    voice_description = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="npcs")
    location = relationship("Location", back_populates="npcs")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(200), nullable=False, index=True)
    type = Column(String(50))  # settlement, dungeon, wilderness, structure, region
    parent_location_id = Column(Integer, ForeignKey("locations.id"))
    population = Column(Integer)
    demographics = Column(JSON)  # Object with demographic data
    government_type = Column(String(100))
    economic_status = Column(String(100))
    notable_features = Column(JSON)  # Array of strings
    description = Column(Text)
    history = Column(Text)
    current_events = Column(JSON)  # Array of current event objects
    defenses = Column(Text)
    trade_goods = Column(JSON)  # Array of trade good objects
    connected_locations = Column(JSON)  # Array of travel route objects
    status = Column(String(50), default="draft")  # draft, active, historical, destroyed
    visibility = Column(String(50), default="dm_only")  # dm_only, player_known, partially_known
    map_image_path = Column(String(500))
    ambient_description = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="locations")
    parent_location = relationship("Location", remote_side=[id])
    child_locations = relationship("Location")
    npcs = relationship("NPC", back_populates="location")

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(200), nullable=False, index=True)
    type = Column(String(50))  # guild, government, religion, criminal, military, academic, merchant
    scope = Column(String(50))  # local, regional, national, international
    headquarters_location_id = Column(Integer, ForeignKey("locations.id"))
    leader_npc_id = Column(Integer, ForeignKey("npcs.id"))
    goals = Column(JSON)  # Array of goal strings
    methods = Column(JSON)  # Array of method strings
    resources = Column(Text)
    influence_level = Column(String(50))
    membership_size = Column(String(50))
    notable_members = Column(JSON)  # Array of NPC IDs
    allies = Column(JSON)  # Array of Organization IDs
    enemies = Column(JSON)  # Array of Organization IDs
    reputation = Column(Text)
    status = Column(String(50), default="draft")  # draft, active, historical, disbanded
    visibility = Column(String(50), default="dm_only")  # dm_only, player_known, partially_known
    symbol_image_path = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="organizations")

class PlotHook(Base):
    __tablename__ = "plot_hooks"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    hook_type = Column(String(50))  # main_quest, side_quest, personal, political, mystery, combat, social
    urgency = Column(String(50))  # immediate, urgent, moderate, background
    complexity = Column(String(50))  # simple, moderate, complex, epic
    related_npcs = Column(JSON)  # Array of NPC IDs
    related_locations = Column(JSON)  # Array of Location IDs
    related_organizations = Column(JSON)  # Array of Organization IDs
    prerequisites = Column(JSON)  # Array of prerequisite objects
    rewards = Column(JSON)  # Reward object
    consequences = Column(JSON)  # Consequence object
    status = Column(String(50), default="draft")  # draft, available, active, completed, failed, abandoned
    visibility = Column(String(50), default="dm_only")  # dm_only, player_known, partially_known
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="plot_hooks")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))  # historical, current, scheduled, recurring
    date = Column(String(100))  # In-world date
    location_id = Column(Integer, ForeignKey("locations.id"))
    participants = Column(JSON)  # Array of NPC/Organization IDs with types
    causes = Column(JSON)  # Array of cause objects
    effects = Column(JSON)  # Array of effect objects
    visibility = Column(String(50), default="dm_only")  # dm_only, player_known, partially_known
    status = Column(String(50), default="draft")  # draft, active, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="events")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(200), nullable=False, index=True)
    type = Column(String(50))  # weapon, armor, tool, treasure, consumable, quest_item, artifact
    rarity = Column(String(50))  # common, uncommon, rare, very_rare, legendary, artifact
    description = Column(Text)
    mechanical_effects = Column(JSON)  # Game mechanics object
    history = Column(Text)
    current_owner_id = Column(Integer, ForeignKey("npcs.id"))
    current_location_id = Column(Integer, ForeignKey("locations.id"))
    value = Column(Integer)  # Value in gold pieces
    weight = Column(Integer)  # Weight in pounds
    attunement_required = Column(Boolean, default=False)
    status = Column(String(50), default="draft")  # draft, active, lost, destroyed
    visibility = Column(String(50), default="dm_only")  # dm_only, player_known, partially_known
    image_path = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="items")

class Idea(Base):
    __tablename__ = "ideas_inbox"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="raw_idea")  # raw_idea, developing, ready_to_implement, implemented
    idea_type = Column(String(50))  # npc, location, plot_hook, lore, item, organization, event
    priority = Column(String(20), default="medium")  # low, medium, high
    ai_session_id = Column(Integer)  # Will be used when AI is added
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="ideas_inbox")