# DM Toolkit - Architecture Document

## System Overview

The DM Toolkit follows a modern three-tier architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Svelte)      │◄──►│   (FastAPI)     │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • UI Components │    │ • REST API      │    │ • Claude API    │
│ • State Mgmt    │    │ • Business      │    │ • File Storage  │
│ • Routing       │    │   Logic         │    │                 │
│ • AI Chat UI    │    │ • Auth          │    │                 │
└─────────────────┘    │ • AI Integration│    └─────────────────┘
                       │ • Data Access   │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite/PG)   │
                       │                 │
                       │ • Campaign Data │
                       │ • User Data     │
                       │ • Session Logs  │
                       └─────────────────┘
```

## Frontend Architecture (Svelte)

### Application Structure
```
src/
├── lib/
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   ├── campaign/           # Campaign-specific components
│   │   ├── ai/                 # AI chat interface
│   │   └── forms/              # Form components for data entry
│   ├── stores/                 # Svelte stores for state management
│   ├── api/                    # API client functions
│   ├── types/                  # TypeScript type definitions
│   └── utils/                  # Utility functions
├── routes/                     # SvelteKit routes
│   ├── auth/                   # Authentication pages
│   ├── campaigns/              # Campaign management
│   ├── [campaignId]/           # Campaign-specific routes
│   │   ├── npcs/
│   │   ├── locations/
│   │   ├── organizations/
│   │   ├── plot-hooks/
│   │   ├── events/
│   │   ├── items/
│   │   ├── ideas/
│   │   └── ai-chat/
│   └── admin/                  # Admin interface
└── app.html                    # Main HTML template
```

### State Management
- **Svelte Stores**: For global application state
- **Campaign Store**: Current campaign data and context
- **Auth Store**: User authentication state
- **AI Chat Store**: Chat history and session management
- **UI Store**: Theme, modals, notifications

### Key Frontend Components

#### AI Chat Interface
```svelte
<AIChat 
  campaignId={campaign.id}
  onElementGenerated={handleElementGeneration}
  sessionHistory={chatStore.currentSession}
/>
```

#### Element Form Components
```svelte
<NPCForm 
  npc={draftNPC}
  mode="create|edit"
  onSave={handleSave}
  onCancel={handleCancel}
/>
```

#### Relationship Visualizer
```svelte
<RelationshipMap 
  elements={allCampaignElements}
  focusElement={selectedElement}
  onElementClick={navigateToElement}
/>
```

## Backend Architecture (FastAPI)

### Project Structure
```
app/
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration management
├── database.py                 # Database connection and setup
├── auth/
│   ├── __init__.py
│   ├── router.py               # Authentication endpoints
│   ├── models.py               # Auth data models
│   ├── schemas.py              # Pydantic schemas
│   └── utils.py                # JWT utilities, password hashing
├── campaigns/
│   ├── __init__.py
│   ├── router.py               # Campaign CRUD endpoints
│   ├── models.py               # Campaign database models
│   ├── schemas.py              # Request/response schemas
│   └── service.py              # Business logic
├── world_elements/
│   ├── __init__.py
│   ├── npcs/
│   │   ├── router.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── locations/
│   ├── organizations/
│   ├── plot_hooks/
│   ├── events/
│   └── items/
├── ai/
│   ├── __init__.py
│   ├── router.py               # AI interaction endpoints
│   ├── client.py               # Claude API client
│   ├── prompts.py              # Prompt templates
│   ├── processors.py           # Response processing
│   └── context.py              # Campaign context management
├── ideas/
│   ├── __init__.py
│   ├── router.py               # Ideas inbox endpoints
│   ├── models.py
│   ├── schemas.py
│   └── service.py
├── sessions/
│   ├── __init__.py
│   ├── router.py               # Session notes endpoints
│   ├── models.py
│   ├── schemas.py
│   └── service.py
├── global_data/
│   ├── __init__.py
│   ├── router.py               # Monster/spell templates
│   ├── models.py
│   └── schemas.py
├── files/
│   ├── __init__.py
│   ├── router.py               # File upload/serving
│   └── storage.py              # File management utilities
├── core/
│   ├── __init__.py
│   ├── dependencies.py         # Common dependencies
│   ├── exceptions.py           # Custom exceptions
│   ├── middleware.py           # Custom middleware
│   └── utils.py                # Utility functions
└── tests/
    ├── conftest.py             # Test configuration
    ├── test_auth.py
    ├── test_campaigns.py
    ├── test_ai.py
    └── ...
```

### API Layer Design

#### RESTful Endpoints
```python
# Example endpoint structure
@router.get("/campaigns/{campaign_id}/npcs", response_model=List[NPCResponse])
async def get_npcs(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    return npc_service.get_npcs(db, campaign_id, current_user.id, skip, limit, search)
```

#### Dependency Injection
```python
# Common dependencies
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # JWT validation and user retrieval

async def get_user_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Campaign:
    # Verify user owns/has access to campaign
```

### Business Logic Layer

#### Service Pattern
```python
class NPCService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_npc(self, campaign_id: int, npc_data: NPCCreate, user_id: int) -> NPC:
        # Validation, business rules, database operations
        
    def get_npc_relationships(self, npc_id: int) -> List[Relationship]:
        # Complex queries for relationship mapping
        
    def update_npc_from_ai(self, npc_id: int, ai_suggestions: dict) -> NPC:
        # AI-driven updates with validation
```

## Database Architecture

### Schema Design Principles
- **Normalization**: Proper relational design with foreign keys
- **Flexibility**: JSON fields for complex, variable data
- **Performance**: Strategic indexing for common queries
- **Integrity**: Constraints and validation at database level

### Key Relationships
```sql
-- Core relationship patterns
Users 1:N Campaigns
Campaigns 1:N WorldElements
WorldElements M:N Relationships (self-referencing)
Campaigns 1:N AIChatsessions
AIChatSessions 1:N GeneratedElements
```

### Database Indexes
```sql
-- Performance-critical indexes
CREATE INDEX idx_npcs_campaign_id ON npcs(campaign_id);
CREATE INDEX idx_npcs_location_id ON npcs(location_id);
CREATE INDEX idx_npcs_name ON npcs(name);
CREATE INDEX idx_locations_campaign_id ON locations(campaign_id);
CREATE INDEX idx_locations_type ON locations(type);
CREATE INDEX idx_ideas_status ON ideas_inbox(status);
CREATE INDEX idx_ideas_campaign_id ON ideas_inbox(campaign_id);

-- Full-text search indexes (PostgreSQL)
CREATE INDEX idx_npcs_search ON npcs USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

## AI Integration Architecture

### Claude API Integration
```python
class ClaudeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    async def generate_content(
        self,
        prompt: str,
        campaign_context: CampaignContext,
        conversation_history: List[Message]
    ) -> ClaudeResponse:
        # Construct full prompt with context
        # Make API call
        # Process and validate response
```

### Context Management
```python
class CampaignContext:
    def __init__(self, campaign_id: int, db: Session):
        self.campaign_id = campaign_id
        self.db = db
    
    def get_context_summary(self) -> str:
        # Summarize campaign state for AI
        # Include recent NPCs, locations, plot hooks
        # Format for prompt injection
    
    def get_relevant_elements(self, topic: str) -> List[WorldElement]:
        # Semantic search for relevant world elements
        # Used for focused context in specific conversations
```

### Prompt Engineering
```python
# Prompt templates with context injection
NPC_GENERATION_PROMPT = """
You are helping a DM create an NPC for their campaign: {campaign_name}

Current campaign context:
- World: {world_summary}
- Recent NPCs: {recent_npcs}
- Current location: {current_location}
- Active plot hooks: {active_plots}

User request: {user_input}

Generate a detailed NPC that fits this world...
"""
```

## Data Flow Architecture

### User Action → Database Update
```
1. User interacts with UI component
2. Component calls API client function
3. API client sends HTTP request to backend
4. FastAPI route handler validates request
5. Service layer applies business logic
6. Database operation executed
7. Response sent back through layers
8. UI updates with new state
```

### AI Content Generation Flow
```
1. User starts AI chat session
2. Frontend sends message to /ai/chat endpoint
3. Backend retrieves campaign context
4. Prompt constructed with context + user message
5. Claude API called with full prompt
6. AI response processed and parsed
7. Suggested elements returned to frontend
8. User reviews in draft form
9. User confirms → elements saved to database
10. AI context updated for next interaction
```

## Security Architecture

### Authentication Flow
```
1. User login → credentials validated
2. JWT token generated and returned
3. Token included in subsequent requests
4. Middleware validates token on protected routes
5. User context available in route handlers
```

### Authorization Patterns
```python
# Campaign ownership verification
def verify_campaign_access(campaign_id: int, user_id: int, db: Session):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == user_id
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign
```

### Data Validation
```python
# Pydantic schemas for request validation
class NPCCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=10000)
    personality_traits: List[str] = Field(default_factory=list, max_items=10)
    
    @validator('personality_traits')
    def validate_traits(cls, v):
        return [trait.strip() for trait in v if trait.strip()]
```

## File Storage Architecture

### Local Storage (Initial)
```
uploads/
├── campaigns/
│   └── {campaign_id}/
│       ├── npcs/
│       │   └── {npc_id}/
│       │       ├── portrait.jpg
│       │       └── sketch.png
│       ├── locations/
│       └── items/
└── temp/                       # Temporary uploads
```

### File Management Service
```python
class FileStorageService:
    def __init__(self, base_path: str):
        self.base_path = base_path
    
    async def store_file(
        self,
        file: UploadFile,
        category: str,
        entity_id: int,
        campaign_id: int
    ) -> str:
        # Validate file type and size
        # Generate unique filename
        # Store in appropriate directory
        # Return file path/URL
    
    def get_file_url(self, file_path: str) -> str:
        # Generate serving URL for file
```

## Caching Strategy

### Application-Level Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_campaign_summary(campaign_id: int) -> CampaignSummary:
    # Cache frequently accessed campaign data
    
# Redis for session storage (future)
class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_ai_context(self, campaign_id: int) -> Optional[str]:
        return await self.redis.get(f"ai_context:{campaign_id}")
```

## Error Handling Architecture

### Exception Hierarchy
```python
class DMToolkitException(Exception):
    """Base exception for all application errors"""
    pass

class ValidationError(DMToolkitException):
    """Data validation errors"""
    pass

class AuthenticationError(DMToolkitException):
    """Authentication failures"""
    pass

class AuthorizationError(DMToolkitException):
    """Authorization failures"""
    pass

class AIServiceError(DMToolkitException):
    """AI service integration errors"""
    pass
```

### Global Exception Handler
```python
@app.exception_handler(DMToolkitException)
async def handle_application_error(request: Request, exc: DMToolkitException):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "type": type(exc).__name__}
    )
```

## Testing Architecture

### Test Structure
```
tests/
├── unit/
│   ├── test_services/
│   ├── test_models/
│   └── test_utils/
├── integration/
│   ├── test_api/
│   ├── test_database/
│   └── test_ai_integration/
├── e2e/
│   ├── test_user_workflows/
│   └── test_ai_workflows/
└── fixtures/
    ├── sample_campaigns.py
    └── mock_ai_responses.py
```

### Test Database Strategy
```python
# Separate test database with fixtures
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///test.db")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        os.remove("test.db")
```

## Performance Considerations

### Database Optimization
- Connection pooling for concurrent requests
- Query optimization with EXPLAIN ANALYZE
- Pagination for large result sets
- Bulk operations for batch AI generation

### Frontend Performance
- Lazy loading for large datasets
- Component-level code splitting
- Image optimization and lazy loading
- Debounced search inputs

### AI Integration Performance
- Response streaming for long AI responses
- Request queuing for batch operations
- Caching of AI-generated content
- Graceful degradation when AI unavailable

## Deployment Architecture

### Development Environment
```
├── Docker Compose setup
│   ├── app container (FastAPI)
│   ├── database container (PostgreSQL)
│   └── frontend dev server (Vite)
├── Local SQLite for rapid development
└── Hot reload for both frontend and backend
```

### Production Considerations
```
├── Container orchestration (Docker)
├── Reverse proxy (Nginx)
├── Database (PostgreSQL with backups)
├── File storage (local → cloud migration path)
├── Monitoring and logging
└── SSL/TLS termination
```

## Scalability Considerations

### Horizontal Scaling Points
- Stateless API design for load balancing
- Database read replicas for query scaling
- CDN for static file serving
- Microservice extraction for AI processing

### Performance Monitoring
- API response time tracking
- Database query performance
- AI service response times
- User session analytics

## Technology Decisions Rationale

### Svelte Frontend
- **Pros**: Excellent performance, small bundle size, great DX
- **Cons**: Smaller ecosystem than React/Vue
- **Decision**: Performance and simplicity align with project needs

### FastAPI Backend
- **Pros**: Excellent async support, automatic API docs, Python ecosystem
- **Cons**: Relatively new framework
- **Decision**: AI integration libraries available in Python

### SQLite → PostgreSQL Migration
- **Phase 1**: SQLite for rapid development and MVP
- **Phase 2**: PostgreSQL for production features (full-text search, JSON queries)
- **Migration strategy**: SQLAlchemy abstracts database differences

This architecture provides a solid foundation for the DM Toolkit while maintaining flexibility for future enhancements and scaling requirements.