# DM Toolkit - Requirements Document

## Project Overview
A comprehensive dungeon master toolkit that combines world-building, campaign management, and AI-assisted content creation. The system helps DMs create lived-in worlds through intelligent content generation and robust data management.

## Technology Stack
- **Frontend**: Svelte
- **Backend**: Python/FastAPI
- **Database**: SQLite (initial), PostgreSQL (production)
- **File Storage**: Local filesystem (initial)
- **AI Integration**: Claude API
- **Authentication**: JWT-based

## Core User Workflows

### 1. Idea Generation & Management
- DM opens AI chat interface
- Discusses ideas conversationally with AI assistant
- AI suggests specific database entries based on conversation
- DM reviews and edits generated content in draft forms
- Content is saved to appropriate database tables

### 2. World Building
- Create and manage campaigns
- Build interconnected world elements (NPCs, locations, organizations)
- Track relationships and dependencies between elements
- Maintain consistency across campaign elements

### 3. Session Management
- Quick database lookups during gameplay
- Note-taking and session logging
- Real-time world state updates based on player actions

## Database Schema

### Core Tables

#### Users
- `id` (Primary Key)
- `email` (Unique)
- `password_hash`
- `username`
- `created_at`
- `updated_at`

#### Campaigns
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `name`
- `description`
- `world_name`
- `current_date` (in-world calendar)
- `created_at`
- `updated_at`

#### Ideas Inbox
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `content` (Raw idea text)
- `status` (enum: 'raw_idea', 'developing', 'ready_to_implement', 'implemented')
- `idea_type` (enum: 'npc', 'location', 'plot_hook', 'lore', 'item', 'organization', 'event')
- `priority` (enum: 'low', 'medium', 'high')
- `ai_session_id` (Reference to chat session)
- `notes`
- `created_at`
- `updated_at`

### World Element Tables

#### NPCs
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `name`
- `race`
- `gender`
- `age`
- `occupation`
- `location_id` (Foreign Key to Locations)
- `personality_traits` (JSON array)
- `ideals`
- `bonds`
- `flaws`
- `appearance_description`
- `background`
- `stats` (JSON object for game stats)
- `relationships` (JSON array of relationships to other NPCs)
- `status` (enum: 'draft', 'active', 'historical', 'dead')
- `visibility` (enum: 'dm_only', 'player_known', 'partially_known')
- `image_path`
- `voice_description`
- `notes`
- `created_at`
- `updated_at`

#### Locations
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `name`
- `type` (enum: 'settlement', 'dungeon', 'wilderness', 'structure', 'region')
- `parent_location_id` (Self-referencing for nested locations)
- `population`
- `demographics` (JSON object)
- `government_type`
- `economic_status`
- `notable_features` (JSON array)
- `description`
- `history`
- `current_events` (JSON array)
- `defenses`
- `trade_goods` (JSON array)
- `connected_locations` (JSON array of travel routes)
- `status` (enum: 'draft', 'active', 'historical', 'destroyed')
- `visibility` (enum: 'dm_only', 'player_known', 'partially_known')
- `map_image_path`
- `ambient_description`
- `notes`
- `created_at`
- `updated_at`

#### Organizations
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `name`
- `type` (enum: 'guild', 'government', 'religion', 'criminal', 'military', 'academic', 'merchant')
- `scope` (enum: 'local', 'regional', 'national', 'international')
- `headquarters_location_id` (Foreign Key to Locations)
- `leader_npc_id` (Foreign Key to NPCs)
- `goals` (JSON array)
- `methods` (JSON array)
- `resources`
- `influence_level`
- `membership_size`
- `notable_members` (JSON array of NPC IDs)
- `allies` (JSON array of Organization IDs)
- `enemies` (JSON array of Organization IDs)
- `reputation`
- `status` (enum: 'draft', 'active', 'historical', 'disbanded')
- `visibility` (enum: 'dm_only', 'player_known', 'partially_known')
- `symbol_image_path`
- `notes`
- `created_at`
- `updated_at`

#### Plot Hooks
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `title`
- `description`
- `hook_type` (enum: 'main_quest', 'side_quest', 'personal', 'political', 'mystery', 'combat', 'social')
- `urgency` (enum: 'immediate', 'urgent', 'moderate', 'background')
- `complexity` (enum: 'simple', 'moderate', 'complex', 'epic')
- `related_npcs` (JSON array of NPC IDs)
- `related_locations` (JSON array of Location IDs)
- `related_organizations` (JSON array of Organization IDs)
- `prerequisites` (JSON array)
- `rewards` (JSON object)
- `consequences` (JSON object)
- `status` (enum: 'draft', 'available', 'active', 'completed', 'failed', 'abandoned')
- `visibility` (enum: 'dm_only', 'player_known', 'partially_known')
- `notes`
- `created_at`
- `updated_at`

#### Events
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `title`
- `description`
- `event_type` (enum: 'historical', 'current', 'scheduled', 'recurring')
- `date` (in-world date)
- `location_id` (Foreign Key to Locations)
- `participants` (JSON array of NPC/Organization IDs)
- `causes` (JSON array)
- `effects` (JSON array)
- `visibility` (enum: 'dm_only', 'player_known', 'partially_known')
- `status` (enum: 'draft', 'active', 'completed', 'cancelled')
- `notes`
- `created_at`
- `updated_at`

#### Items
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `name`
- `type` (enum: 'weapon', 'armor', 'tool', 'treasure', 'consumable', 'quest_item', 'artifact')
- `rarity` (enum: 'common', 'uncommon', 'rare', 'very_rare', 'legendary', 'artifact')
- `description`
- `mechanical_effects` (JSON object)
- `history`
- `current_owner_id` (Foreign Key to NPCs, nullable)
- `current_location_id` (Foreign Key to Locations, nullable)
- `value` (in gold pieces)
- `weight`
- `attunement_required` (boolean)
- `status` (enum: 'draft', 'active', 'lost', 'destroyed')
- `visibility` (enum: 'dm_only', 'player_known', 'partially_known')
- `image_path`
- `notes`
- `created_at`
- `updated_at`

### Supporting Tables

#### AI Chat Sessions
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `session_name`
- `messages` (JSON array of chat messages)
- `generated_elements` (JSON array of element IDs created in this session)
- `created_at`
- `updated_at`

#### Session Notes
- `id` (Primary Key)
- `campaign_id` (Foreign Key)
- `session_date`
- `session_number`
- `summary`
- `events` (JSON array)
- `npc_interactions` (JSON array)
- `locations_visited` (JSON array)
- `items_gained_lost` (JSON array)
- `plot_advancement` (JSON array)
- `notes`
- `created_at`
- `updated_at`

#### Global Elements

#### Monster Templates
- `id` (Primary Key)
- `name`
- `type`
- `challenge_rating`
- `stats` (JSON object)
- `abilities` (JSON array)
- `description`
- `source` (rulebook reference)

#### Spell Templates
- `id` (Primary Key)
- `name`
- `level`
- `school`
- `components`
- `casting_time`
- `range`
- `duration`
- `description`
- `source` (rulebook reference)

## Authentication & User Management

### Authentication Requirements
- JWT-based authentication
- Email/password registration and login
- Password reset functionality
- Session management
- Role-based access control

### User Roles
- **User**: Can create and manage their own campaigns
- **Admin**: System administration (future feature)

### Security Requirements
- Password hashing with bcrypt
- JWT token expiration and refresh
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## AI Integration Requirements

### Claude API Integration
- Conversational interface for brainstorming
- Context awareness of current campaign data
- Intelligent content categorization
- Batch content generation capabilities
- Consistent personality and tone

### AI Capabilities
- **NPC Generation**: Create detailed NPCs with personality, background, and relationships
- **Location Creation**: Generate settlements, dungeons, and regions with appropriate details
- **Plot Hook Development**: Create interconnected story elements
- **Relationship Mapping**: Suggest connections between existing world elements
- **Consequence Prediction**: Analyze potential impacts of player actions
- **Content Expansion**: Elaborate on existing world elements

### AI Workflow
1. User initiates chat session
2. AI has read access to all campaign data
3. Conversational brainstorming with intelligent suggestions
4. AI proposes specific database entries in JSON format
5. User reviews and edits in draft forms
6. User confirms and saves to database
7. AI updates context for future conversations

### Content Generation Features
- Single element creation (one NPC, location, etc.)
- Batch generation (5 NPCs for a town)
- Relationship suggestion between existing elements
- Plot hook generation based on current world state
- Event consequence modeling

## User Interface Requirements

### Core Pages
- **Dashboard**: Campaign overview, recent activity, quick stats
- **Campaign Management**: Create/edit campaigns, settings
- **AI Chat Interface**: Conversational world building
- **Element Browsers**: Searchable lists for NPCs, locations, etc.
- **Element Detail Pages**: Full CRUD for each element type
- **Ideas Inbox**: Manage and process brainstormed ideas
- **Session Management**: Note-taking and session logging

### UI/UX Requirements
- Responsive design (desktop-first, mobile-friendly)
- Dark/light theme support
- Intuitive navigation between related elements
- Quick search functionality
- Drag-and-drop for organizing ideas
- Rich text editing for descriptions
- Image upload and preview
- Form validation with helpful error messages

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support

## API Requirements

### RESTful API Design
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response format
- Proper HTTP status codes
- Error handling with meaningful messages
- API versioning strategy

### Key Endpoints
- `/auth/*` - Authentication endpoints
- `/campaigns/*` - Campaign management
- `/campaigns/{id}/npcs/*` - NPC management
- `/campaigns/{id}/locations/*` - Location management
- `/campaigns/{id}/organizations/*` - Organization management
- `/campaigns/{id}/plot-hooks/*` - Plot hook management
- `/campaigns/{id}/events/*` - Event management
- `/campaigns/{id}/items/*` - Item management
- `/campaigns/{id}/ideas/*` - Ideas inbox management
- `/campaigns/{id}/sessions/*` - Session notes
- `/ai/chat/*` - AI interaction endpoints
- `/global/monsters/*` - Monster templates
- `/global/spells/*` - Spell templates

### Data Validation
- Pydantic models for request/response validation
- Database constraints for data integrity
- File upload validation (type, size limits)
- User input sanitization

## File Management Requirements

### Image Support
- Upload and store images for NPCs, locations, organizations, items
- Image resizing and optimization
- Supported formats: JPEG, PNG, WebP
- File size limits (5MB per image initially)
- Secure file serving

### Future Media Features
- AI image generation integration
- Audio file support for ambient sounds
- Music library management
- Audio streaming capabilities

## Performance Requirements

### Response Times
- Page loads: < 2 seconds
- API responses: < 500ms
- AI responses: < 10 seconds
- Image uploads: < 5 seconds

### Scalability Considerations
- Database indexing for search performance
- Efficient query patterns
- File storage optimization
- Caching strategy for frequently accessed data

## Testing Requirements

### Unit Testing
- Backend API endpoint testing
- Database model testing
- AI integration testing
- Frontend component testing

### Integration Testing
- End-to-end user workflows
- AI chat session testing
- File upload/download testing
- Authentication flow testing

## Development Phases

### Phase 1: MVP
- Basic authentication
- Campaign creation and management
- Core CRUD operations for NPCs and locations
- Simple AI chat integration
- Ideas inbox functionality

### Phase 2: Enhanced World Building
- All world element types (organizations, plot hooks, events, items)
- Advanced AI features (batch generation, relationship suggestions)
- Image upload support
- Session notes and logging

### Phase 3: Advanced Features
- Global monster/spell databases
- Advanced search and filtering
- Relationship visualization
- Import/export functionality

### Phase 4: Multimedia & Polish
- AI image generation
- Audio/music support
- Advanced UI features
- Performance optimization

## Success Criteria

### Functional Requirements
- Users can create and manage multiple campaigns
- AI assistant successfully generates appropriate content
- All world elements can be created, edited, and deleted
- Ideas workflow from brainstorming to implementation works smoothly
- Search and navigation between elements is intuitive

### Technical Requirements
- System handles concurrent users without performance degradation
- Data integrity is maintained across all operations
- Security measures prevent unauthorized access
- System is maintainable and extensible

### User Experience Requirements
- New users can create their first campaign within 10 minutes
- AI responses feel natural and helpful
- Interface is intuitive without requiring documentation
- System feels fast and responsive during normal use