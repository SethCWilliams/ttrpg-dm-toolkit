# DM Toolkit - API Schema Document

## Database Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

#### campaigns
```sql
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    world_name VARCHAR(200),
    current_date VARCHAR(100), -- In-world calendar date
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
```

#### ideas_inbox
```sql
CREATE TABLE ideas_inbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'raw_idea' CHECK (status IN ('raw_idea', 'developing', 'ready_to_implement', 'implemented')),
    idea_type VARCHAR(50) CHECK (idea_type IN ('npc', 'location', 'plot_hook', 'lore', 'item', 'organization', 'event')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    ai_session_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE INDEX idx_session_notes_campaign_id ON session_notes(campaign_id);
CREATE INDEX idx_session_notes_date ON session_notes(session_date);
```

### Global Tables

#### monster_templates
```sql
CREATE TABLE monster_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(100),
    challenge_rating VARCHAR(20),
    stats JSON, -- Complete stat block
    abilities JSON, -- Special abilities array
    description TEXT,
    source VARCHAR(200), -- Rulebook reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_monsters_name ON monster_templates(name);
CREATE INDEX idx_monsters_cr ON monster_templates(challenge_rating);
CREATE INDEX idx_monsters_type ON monster_templates(type);
```

#### spell_templates
```sql
CREATE TABLE spell_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    level INTEGER,
    school VARCHAR(100),
    components VARCHAR(200),
    casting_time VARCHAR(200),
    range VARCHAR(200),
    duration VARCHAR(200),
    description TEXT,
    source VARCHAR(200), -- Rulebook reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_spells_name ON spell_templates(name);
CREATE INDEX idx_spells_level ON spell_templates(level);
CREATE INDEX idx_spells_school ON spell_templates(school);
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/register
```json
Request:
{
    "email": "dm@example.com",
    "username": "AwesomeDM",
    "password": "securepassword"
}

Response:
{
    "id": 1,
    "email": "dm@example.com",
    "username": "AwesomeDM",
    "created_at": "2025-08-19T10:00:00Z"
}
```

#### POST /auth/login
```json
Request:
{
    "email": "dm@example.com",
    "password": "securepassword"
}

Response:
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "email": "dm@example.com",
        "username": "AwesomeDM"
    }
}
```

#### POST /auth/refresh
```json
Request:
{
    "refresh_token": "refresh_token_here"
}

Response:
{
    "access_token": "new_access_token",
    "token_type": "bearer"
}
```

### Campaign Management Endpoints

#### GET /campaigns
```json
Response:
[
    {
        "id": 1,
        "name": "Curse of Strahd",
        "description": "Gothic horror in Barovia",
        "world_name": "Ravenloft",
        "current_date": "15th of Flamerule, 1491 DR",
        "created_at": "2025-08-01T10:00:00Z",
        "updated_at": "2025-08-19T15:30:00Z"
    }
]
```

#### POST /campaigns
```json
Request:
{
    "name": "Lost Mine of Phandelver",
    "description": "A starter adventure in the Sword Coast",
    "world_name": "Forgotten Realms",
    "current_date": "1st of Mirtul, 1491 DR"
}

Response:
{
    "id": 2,
    "name": "Lost Mine of Phandelver",
    "description": "A starter adventure in the Sword Coast",
    "world_name": "Forgotten Realms",
    "current_date": "1st of Mirtul, 1491 DR",
    "created_at": "2025-08-19T16:00:00Z",
    "updated_at": "2025-08-19T16:00:00Z"
}
```

#### GET /campaigns/{campaign_id}
```json
Response:
{
    "id": 1,
    "name": "Curse of Strahd",
    "description": "Gothic horror in Barovia",
    "world_name": "Ravenloft",
    "current_date": "15th of Flamerule, 1491 DR",
    "stats": {
        "npc_count": 45,
        "location_count": 12,
        "organization_count": 8,
        "plot_hook_count": 15,
        "session_count": 8
    },
    "created_at": "2025-08-01T10:00:00Z",
    "updated_at": "2025-08-19T15:30:00Z"
}
```

### NPC Endpoints

#### GET /campaigns/{campaign_id}/npcs
```json
Query Parameters:
- skip: int = 0
- limit: int = 100
- search: str (optional)
- location_id: int (optional)
- status: str (optional)

Response:
{
    "total": 45,
    "items": [
        {
            "id": 1,
            "name": "Strahd von Zarovich",
            "race": "Vampire",
            "gender": "Male",
            "age": 600,
            "occupation": "Lord of Barovia",
            "location_id": 1,
            "personality_traits": ["Arrogant", "Tragic", "Obsessive"],
            "ideals": "Control and eternal love",
            "bonds": "Tatyana's soul",
            "flaws": "Obsession with Tatyana",
            "appearance_description": "Tall, pale, aristocratic vampire lord",
            "background": "Former noble turned vampire lord...",
            "stats": {
                "AC": 16,
                "HP": 144,
                "speed": "30 ft.",
                "STR": 18,
                "DEX": 15,
                "CON": 15,
                "INT": 20,
                "WIS": 15,
                "CHA": 18
            },
            "relationships": [
                {
                    "target_id": 2,
                    "target_type": "npc",
                    "relationship_type": "obsession",
                    "description": "Obsessed with Ireena as Tatyana reborn"
                }
            ],
            "status": "active",
            "visibility": "player_known",
            "image_path": "/uploads/campaigns/1/npcs/1/portrait.jpg",
            "voice_description": "Deep, aristocratic, with Romanian accent",
            "notes": "Main antagonist of the campaign",
            "created_at": "2025-08-01T10:00:00Z",
            "updated_at": "2025-08-15T14:20:00Z"
        }
    ]
}
```

#### POST /campaigns/{campaign_id}/npcs
```json
Request:
{
    "name": "Ireena Kolyana",
    "race": "Human",
    "gender": "Female",
    "age": 24,
    "occupation": "Noble",
    "location_id": 2,
    "personality_traits": ["Brave", "Kind", "Determined"],
    "ideals": "Protecting her people",
    "bonds": "The people of Barovia",
    "flaws": "Sometimes too trusting",
    "appearance_description": "Beautiful young woman with auburn hair",
    "background": "Adopted daughter of the burgomaster...",
    "status": "active",
    "visibility": "player_known"
}

Response: (Same structure as GET response for single NPC)
```

#### PUT /campaigns/{campaign_id}/npcs/{npc_id}
```json
Request: (Same as POST, but all fields optional)

Response: (Updated NPC object)
```

#### DELETE /campaigns/{campaign_id}/npcs/{npc_id}
```json
Response:
{
    "message": "NPC deleted successfully"
}
```

### Location Endpoints

#### GET /campaigns/{campaign_id}/locations
```json
Query Parameters:
- skip: int = 0
- limit: int = 100
- search: str (optional)
- type: str (optional)
- parent_location_id: int (optional)

Response:
{
    "total": 12,
    "items": [
        {
            "id": 1,
            "name": "Castle Ravenloft",
            "type": "structure",
            "parent_location_id": null,
            "population": 50,
            "demographics": {
                "undead": 45,
                "human": 5
            },
            "government_type": "Autocracy",
            "economic_status": "Declining",
            "notable_features": [
                "Massive gothic castle",
                "Heart of Svalich Wood",
                "Strahd's domain"
            ],
            "description": "A massive gothic castle perched on a cliff...",
            "history": "Built by Strahd von Zarovich centuries ago...",
            "current_events": [
                {
                    "event": "Strahd's bride search",
                    "description": "Strahd actively seeks Ireena"
                }
            ],
            "defenses": "Supernatural protections, undead guardians",
            "trade_goods": [],
            "connected_locations": [
                {
                    "location_id": 2,
                    "travel_time": "4 hours",
                    "difficulty": "hard",
                    "description": "Treacherous mountain path"
                }
            ],
            "status": "active",
            "visibility": "player_known",
            "map_image_path": "/uploads/campaigns/1/locations/1/map.jpg",
            "ambient_description": "Cold, oppressive atmosphere with howling winds",
            "notes": "Central location for the campaign",
            "created_at": "2025-08-01T10:00:00Z",
            "updated_at": "2025-08-10T11:15:00Z"
        }
    ]
}
```

### Organization Endpoints

#### GET /campaigns/{campaign_id}/organizations
```json
Response:
{
    "total": 8,
    "items": [
        {
            "id": 1,
            "name": "The Order of the Silver Dragon",
            "type": "military",
            "scope": "regional",
            "headquarters_location_id": 3,
            "leader_npc_id": 5,
            "goals": [
                "Protect innocent civilians",
                "Fight against undead threats",
                "Restore hope to Barovia"
            ],
            "methods": [
                "Armed patrols",
                "Information gathering",
                "Strategic alliances"
            ],
            "resources": "Limited weapons and supplies",
            "influence_level": "Minor",
            "membership_size": "Small (12 members)",
            "notable_members": [5, 6, 7],
            "allies": [],
            "enemies": [2],
            "reputation": "Respected by common folk",
            "status": "active",
            "visibility": "player_known",
            "symbol_image_path": "/uploads/campaigns/1/organizations/1/symbol.png",
            "notes": "Potential ally for the party",
            "created_at": "2025-08-05T14:00:00Z",
            "updated_at": "2025-08-18T09:30:00Z"
        }
    ]
}
```

### Plot Hook Endpoints

#### GET /campaigns/{campaign_id}/plot-hooks
```json
Response:
{
    "total": 15,
    "items": [
        {
            "id": 1,
            "title": "The Missing Bride",
            "description": "Strahd seeks a new bride and has set his sights on Ireena",
            "hook_type": "main_quest",
            "urgency": "urgent",
            "complexity": "epic",
            "related_npcs": [1, 2],
            "related_locations": [1, 2],
            "related_organizations": [],
            "prerequisites": [
                {
                    "type": "location_visited",
                    "target_id": 2,
                    "description": "Party must visit Village of Barovia"
                }
            ],
            "rewards": {
                "experience": 5000,
                "items": ["Holy Symbol of Ravenkind"],
                "story": "Freedom from Barovia's curse"
            },
            "consequences": {
                "success": "Barovia is freed from Strahd's curse",
                "failure": "Ireena becomes Strahd's bride, eternal darkness"
            },
            "status": "active",
            "visibility": "partially_known",
            "notes": "Central plot of the campaign",
            "created_at": "2025-08-01T10:00:00Z",
            "updated_at": "2025-08-12T16:45:00Z"
        }
    ]
}
```

### Ideas Inbox Endpoints

#### GET /campaigns/{campaign_id}/ideas
```json
Query Parameters:
- status: str (optional)
- idea_type: str (optional)
- priority: str (optional)

Response:
{
    "total": 23,
    "items": [
        {
            "id": 1,
            "content": "A mysterious traveling merchant who appears only during full moons",
            "status": "ready_to_implement",
            "idea_type": "npc",
            "priority": "medium",
            "ai_session_id": 5,
            "notes": "Could be a werewolf or have connections to lycanthropes",
            "created_at": "2025-08-18T09:00:00Z",
            "updated_at": "2025-08-19T10:30:00Z"
        }
    ]
}
```

#### POST /campaigns/{campaign_id}/ideas
```json
Request:
{
    "content": "Ancient library hidden beneath the tavern",
    "idea_type": "location",
    "priority": "high",
    "notes": "Could contain information about Strahd's past"
}

Response: (Created idea object)
```

#### PUT /campaigns/{campaign_id}/ideas/{idea_id}
```json
Request:
{
    "status": "implemented",
    "notes": "Converted to Location: Hidden Library"
}

Response: (Updated idea object)
```

### AI Chat Endpoints

#### POST /campaigns/{campaign_id}/ai/chat
```json
Request:
{
    "message": "I need some NPCs for the tavern in Vallaki",
    "session_id": 5  // Optional, creates new session if not provided
}

Response:
{
    "session_id": 5,
    "ai_response": "I'd be happy to help create some NPCs for the tavern in Vallaki! Given the oppressive atmosphere of Barovia and Vallaki's unique situation...",
    "suggested_elements": [
        {
            "type": "npc",
            "data": {
                "name": "Dmitri Volkov",
                "race": "Human",
                "occupation": "Tavern keeper",
                "personality_traits": ["Nervous", "Overly cheerful"],
                "background": "Desperately maintains false happiness..."
            }
        }
    ]
}
```

#### GET /campaigns/{campaign_id}/ai/sessions
```json
Response:
[
    {
        "id": 5,
        "session_name": "Vallaki NPCs Brainstorm",
        "message_count": 12,
        "generated_elements_count": 5,
        "created_at": "2025-08-19T09:00:00Z",
        "updated_at": "2025-08-19T10:30:00Z"
    }
]
```

#### GET /campaigns/{campaign_id}/ai/sessions/{session_id}
```json
Response:
{
    "id": 5,
    "session_name": "Vallaki NPCs Brainstorm",
    "messages": [
        {
            "role": "user",
            "content": "I need some NPCs for the tavern in Vallaki",
            "timestamp": "2025-08-19T09:00:00Z"
        },
        {
            "role": "assistant",
            "content": "I'd be happy to help create some NPCs...",
            "timestamp": "2025-08-19T09:00:15Z"
        }
    ],
    "generated_elements": [
        {
            "type": "npc",
            "id": 15,
            "name": "Dmitri Volkov",
            "created_from_message": 2
        }
    ]
}
```

### Session Notes Endpoints

#### GET /campaigns/{campaign_id}/sessions
```json
Response:
[
    {
        "id": 1,
        "session_date": "2025-08-15",
        "session_number": 8,
        "summary": "Party arrived in Vallaki and met the burgomaster",
        "created_at": "2025-08-15T22:00:00Z"
    }
]
```

#### POST /campaigns/{campaign_id}/sessions
```json
Request:
{
    "session_date": "2025-08-19",
    "session_number": 9,
    "summary": "Party investigated the Baron's mansion",
    "events": [
        {
            "type": "social_encounter",
            "description": "Met Baron Vallakovich",
            "npcs_involved": [8],
            "outcome": "Successful persuasion"
        }
    ],
    "npc_interactions": [
        {
            "npc_id": 8,
            "interaction_type": "conversation",
            "description": "Learned about the festival preparations",
            "relationship_change": "neutral_to_friendly"
        }
    ],
    "locations_visited": [4],
    "plot_advancement": [
        {
            "plot_hook_id": 3,
            "advancement": "Discovered Baron's obsession with festivals"
        }
    ]
}

Response: (Created session object)
```

### File Upload Endpoints

#### POST /campaigns/{campaign_id}/upload
```json
Request: (Multipart form data)
- file: (image file)
- entity_type: "npc" | "location" | "organization" | "item"
- entity_id: number

Response:
{
    "file_path": "/uploads/campaigns/1/npcs/15/portrait.jpg",
    "file_url": "http://localhost:8000/files/campaigns/1/npcs/15/portrait.jpg",
    "file_size": 245760,
    "content_type": "image/jpeg"
}
```

#### GET /files/{file_path}
```
Response: (File content with appropriate headers)
```

### Global Data Endpoints

#### GET /global/monsters
```json
Query Parameters:
- search: str (optional)
- challenge_rating: str (optional)
- type: str (optional)

Response:
[
    {
        "id": 1,
        "name": "Vampire",
        "type": "Undead",
        "challenge_rating": "13",
        "stats": {
            "AC": 16,
            "HP": 144,
            "speed": "30 ft.",
            "STR": 18,
            "DEX": 15,
            "CON": 15,
            "INT": 17,
            "WIS": 15,
            "CHA": 18
        },
        "abilities": [
            {
                "name": "Shapechanger",
                "description": "The vampire can use its action to polymorph..."
            }
        ],
        "description": "Vampires are undead creatures that feed on blood...",
        "source": "Monster Manual"
    }
]
```

#### GET /global/spells
```json
Query Parameters:
- search: str (optional)
- level: int (optional)
- school: str (optional)

Response:
[
    {
        "id": 1,
        "name": "Fireball",
        "level": 3,
        "school": "Evocation",
        "components": "V, S, M (a tiny ball of bat guano and sulfur)",
        "casting_time": "1 action",
        "range": "150 feet",
        "duration": "Instantaneous",
        "description": "A bright streak flashes from your pointing finger...",
        "source": "Player's Handbook"
    }
]
```

## JSON Schema Definitions

### NPC Relationships
```json
{
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "target_id": {"type": "integer"},
            "target_type": {"type": "string", "enum": ["npc", "organization", "location"]},
            "relationship_type": {"type": "string"},
            "description": {"type": "string"},
            "strength": {"type": "string", "enum": ["weak", "moderate", "strong"]},
            "public_knowledge": {"type": "boolean"}
        },
        "required": ["target_id", "target_type", "relationship_type"]
    }
}
```

### Location Demographics
```json
{
    "type": "object",
    "properties": {
        "total_population": {"type": "integer"},
        "races": {
            "type": "object",
            "patternProperties": {
                "^[a-zA-Z]+$": {"type": "integer"}
            }
        },
        "age_distribution": {
            "type": "object",
            "properties": {
                "children": {"type": "integer"},
                "adults": {"type": "integer"},
                "elderly": {"type": "integer"}
            }
        },
        "social_classes": {
            "type": "object",
            "properties": {
                "nobility": {"type": "integer"},
                "merchants": {"type": "integer"},
                "craftspeople": {"type": "integer"},
                "laborers": {"type": "integer"},
                "poor": {"type": "integer"}
            }
        }
    }
}
```

### Trade Goods
```json
{
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "quantity": {"type": "string"},
            "price": {"type": "number"},
            "rarity": {"type": "string", "enum": ["common", "uncommon", "rare"]},
            "seasonal": {"type": "boolean"},
            "import_export": {"type": "string", "enum": ["import", "export", "both"]}
        },
        "required": ["name", "type"]
    }
}
```

### Item Mechanical Effects
```json
{
    "type": "object",
    "properties": {
        "weapon_properties": {
            "type": "object",
            "properties": {
                "damage": {"type": "string"},
                "damage_type": {"type": "string"},
                "properties": {"type": "array", "items": {"type": "string"}}
            }
        },
        "armor_properties": {
            "type": "object",
            "properties": {
                "ac_base": {"type": "integer"},
                "ac_dex_limit": {"type": "integer"},
                "stealth_disadvantage": {"type": "boolean"}
            }
        },
        "magical_properties": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "charges": {"type": "integer"},
                    "recharge": {"type": "string"}
                }
            }
        }
    }
}
```

## Error Response Format

All API endpoints use consistent error response format:

```json
{
    "error": {
        "type": "ValidationError",
        "message": "Invalid input data",
        "details": {
            "field": "name",
            "code": "required",
            "message": "Name is required"
        }
    },
    "request_id": "req_abc123"
}
```

## API Rate Limiting

Rate limits are applied per user:
- Authentication endpoints: 5 requests per minute
- AI chat endpoints: 20 requests per minute
- All other endpoints: 100 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1692454800
```

This schema provides a comprehensive foundation for the DM Toolkit API, supporting all the features outlined in the requirements while maintaining consistency and extensibility.at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (ai_session_id) REFERENCES ai_chat_sessions(id) ON DELETE SET NULL
);

CREATE INDEX idx_ideas_campaign_id ON ideas_inbox(campaign_id);
CREATE INDEX idx_ideas_status ON ideas_inbox(status);
CREATE INDEX idx_ideas_type ON ideas_inbox(idea_type);
```

### World Element Tables

#### npcs
```sql
CREATE TABLE npcs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    race VARCHAR(100),
    gender VARCHAR(50),
    age INTEGER,
    occupation VARCHAR(200),
    location_id INTEGER,
    personality_traits JSON, -- Array of strings
    ideals TEXT,
    bonds TEXT,
    flaws TEXT,
    appearance_description TEXT,
    background TEXT,
    stats JSON, -- Game statistics object
    relationships JSON, -- Array of relationship objects
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'historical', 'dead')),
    visibility VARCHAR(50) DEFAULT 'dm_only' CHECK (visibility IN ('dm_only', 'player_known', 'partially_known')),
    image_path VARCHAR(500),
    voice_description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

CREATE INDEX idx_npcs_campaign_id ON npcs(campaign_id);
CREATE INDEX idx_npcs_location_id ON npcs(location_id);
CREATE INDEX idx_npcs_name ON npcs(name);
CREATE INDEX idx_npcs_status ON npcs(status);
```

#### locations
```sql
CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('settlement', 'dungeon', 'wilderness', 'structure', 'region')),
    parent_location_id INTEGER,
    population INTEGER,
    demographics JSON, -- Object with demographic data
    government_type VARCHAR(100),
    economic_status VARCHAR(100),
    notable_features JSON, -- Array of strings
    description TEXT,
    history TEXT,
    current_events JSON, -- Array of current event objects
    defenses TEXT,
    trade_goods JSON, -- Array of trade good objects
    connected_locations JSON, -- Array of travel route objects
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'historical', 'destroyed')),
    visibility VARCHAR(50) DEFAULT 'dm_only' CHECK (visibility IN ('dm_only', 'player_known', 'partially_known')),
    map_image_path VARCHAR(500),
    ambient_description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_location_id) REFERENCES locations(id) ON DELETE SET NULL
);

CREATE INDEX idx_locations_campaign_id ON locations(campaign_id);
CREATE INDEX idx_locations_type ON locations(type);
CREATE INDEX idx_locations_parent ON locations(parent_location_id);
CREATE INDEX idx_locations_name ON locations(name);
```

#### organizations
```sql
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('guild', 'government', 'religion', 'criminal', 'military', 'academic', 'merchant')),
    scope VARCHAR(50) CHECK (scope IN ('local', 'regional', 'national', 'international')),
    headquarters_location_id INTEGER,
    leader_npc_id INTEGER,
    goals JSON, -- Array of goal strings
    methods JSON, -- Array of method strings
    resources TEXT,
    influence_level VARCHAR(50),
    membership_size VARCHAR(50),
    notable_members JSON, -- Array of NPC IDs
    allies JSON, -- Array of Organization IDs
    enemies JSON, -- Array of Organization IDs
    reputation TEXT,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'historical', 'disbanded')),
    visibility VARCHAR(50) DEFAULT 'dm_only' CHECK (visibility IN ('dm_only', 'player_known', 'partially_known')),
    symbol_image_path VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (headquarters_location_id) REFERENCES locations(id) ON DELETE SET NULL,
    FOREIGN KEY (leader_npc_id) REFERENCES npcs(id) ON DELETE SET NULL
);

CREATE INDEX idx_organizations_campaign_id ON organizations(campaign_id);
CREATE INDEX idx_organizations_type ON organizations(type);
CREATE INDEX idx_organizations_leader ON organizations(leader_npc_id);
CREATE INDEX idx_organizations_headquarters ON organizations(headquarters_location_id);
```

#### plot_hooks
```sql
CREATE TABLE plot_hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    hook_type VARCHAR(50) CHECK (hook_type IN ('main_quest', 'side_quest', 'personal', 'political', 'mystery', 'combat', 'social')),
    urgency VARCHAR(50) CHECK (urgency IN ('immediate', 'urgent', 'moderate', 'background')),
    complexity VARCHAR(50) CHECK (complexity IN ('simple', 'moderate', 'complex', 'epic')),
    related_npcs JSON, -- Array of NPC IDs
    related_locations JSON, -- Array of Location IDs
    related_organizations JSON, -- Array of Organization IDs
    prerequisites JSON, -- Array of prerequisite objects
    rewards JSON, -- Reward object
    consequences JSON, -- Consequence object
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'available', 'active', 'completed', 'failed', 'abandoned')),
    visibility VARCHAR(50) DEFAULT 'dm_only' CHECK (visibility IN ('dm_only', 'player_known', 'partially_known')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE INDEX idx_plot_hooks_campaign_id ON plot_hooks(campaign_id);
CREATE INDEX idx_plot_hooks_type ON plot_hooks(hook_type);
CREATE INDEX idx_plot_hooks_status ON plot_hooks(status);
CREATE INDEX idx_plot_hooks_urgency ON plot_hooks(urgency);
```

#### events
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) CHECK (event_type IN ('historical', 'current', 'scheduled', 'recurring')),
    date VARCHAR(100), -- In-world date
    location_id INTEGER,
    participants JSON, -- Array of NPC/Organization IDs with types
    causes JSON, -- Array of cause objects
    effects JSON, -- Array of effect objects
    visibility VARCHAR(50) DEFAULT 'dm_only' CHECK (visibility IN ('dm_only', 'player_known', 'partially_known')),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

CREATE INDEX idx_events_campaign_id ON events(campaign_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_events_location ON events(location_id);
```

#### items
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('weapon', 'armor', 'tool', 'treasure', 'consumable', 'quest_item', 'artifact')),
    rarity VARCHAR(50) CHECK (rarity IN ('common', 'uncommon', 'rare', 'very_rare', 'legendary', 'artifact')),
    description TEXT,
    mechanical_effects JSON, -- Game mechanics object
    history TEXT,
    current_owner_id INTEGER,
    current_location_id INTEGER,
    value INTEGER, -- Value in gold pieces
    weight REAL,
    attunement_required BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'lost', 'destroyed')),
    visibility VARCHAR(50) DEFAULT 'dm_only' CHECK (visibility IN ('dm_only', 'player_known', 'partially_known')),
    image_path VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (current_owner_id) REFERENCES npcs(id) ON DELETE SET NULL,
    FOREIGN KEY (current_location_id) REFERENCES locations(id) ON DELETE SET NULL
);

CREATE INDEX idx_items_campaign_id ON items(campaign_id);
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_rarity ON items(rarity);
CREATE INDEX idx_items_owner ON items(current_owner_id);
CREATE INDEX idx_items_location ON items(current_location_id);
```

### Supporting Tables

#### ai_chat_sessions
```sql
CREATE TABLE ai_chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    session_name VARCHAR(200),
    messages JSON, -- Array of chat message objects
    generated_elements JSON, -- Array of element references
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE INDEX idx_ai_sessions_campaign_id ON ai_chat_sessions(campaign_id);
```

#### session_notes
```sql
CREATE TABLE session_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    session_date DATE,
    session_number INTEGER,
    summary TEXT,
    events JSON, -- Array of session event objects
    npc_interactions JSON, -- Array of NPC interaction objects
    locations_visited JSON, -- Array of location IDs
    items_gained_lost JSON, -- Array of item transaction objects
    plot_advancement JSON, -- Array of plot advancement objects
    notes TEXT,
    created_