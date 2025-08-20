# DM Toolkit - User Stories Document

## Epic 1: Campaign Management

### Story 1.1: Campaign Creation
**As a DM**, I want to create a new campaign with basic information, so that I can start organizing my world-building efforts.

**Acceptance Criteria:**
- I can enter a campaign name, description, and world name
- I can set an initial in-world date
- The campaign is saved and appears in my campaigns list
- I am automatically redirected to the campaign dashboard

**Technical Notes:**
- Creates campaign record in database
- Associates campaign with authenticated user
- Generates campaign dashboard with empty stats

---

### Story 1.2: Campaign Dashboard
**As a DM**, I want to see an overview of my campaign data, so that I can quickly understand the current state of my world.

**Acceptance Criteria:**
- I can see counts of NPCs, locations, organizations, plot hooks, events, and items
- I can see my most recent session notes
- I can see recent AI chat activity
- I can quickly navigate to different sections of my campaign

**Technical Notes:**
- Aggregates data from all campaign tables
- Shows recent activity from session notes and AI chats
- Provides quick navigation to major sections

---

### Story 1.3: Multiple Campaign Management
**As a DM**, I want to manage multiple campaigns simultaneously, so that I can run different games for different groups.

**Acceptance Criteria:**
- I can switch between campaigns easily
- Each campaign maintains separate data
- I can create new campaigns without affecting existing ones
- Campaign names and descriptions are clearly differentiated

**Technical Notes:**
- Campaign switcher in main navigation
- All API calls scoped to current campaign
- Proper data isolation between campaigns

---

## Epic 2: AI-Assisted World Building

### Story 2.1: AI Chat Interface
**As a DM**, I want to have a conversational interface with an AI assistant, so that I can brainstorm ideas for my campaign.

**Acceptance Criteria:**
- I can start a new AI chat session
- The AI responds contextually based on my campaign data
- Chat history is preserved within sessions
- I can name sessions for easy reference

**Technical Notes:**
- Integrates with Claude API
- Maintains conversation context
- Stores chat history in database
- Session management for organization

---

### Story 2.2: Campaign-Aware AI Responses
**As a DM**, I want the AI to understand my existing campaign when making suggestions, so that new content fits naturally into my world.

**Acceptance Criteria:**
- AI references existing NPCs, locations, and organizations when relevant
- AI suggests connections to existing world elements
- AI maintains consistency with established lore and tone
- AI avoids contradicting existing campaign elements

**Technical Notes:**
- Campaign context injection into AI prompts
- Retrieval of relevant campaign data for context
- Prompt engineering for consistency
- Context summarization for large campaigns

---

### Story 2.3: AI Content Generation with Review
**As a DM**, I want the AI to generate specific world elements based on our conversation, so that I can quickly create detailed content.

**Acceptance Criteria:**
- AI can generate NPCs, locations, organizations, plot hooks, events, and items
- Generated content is presented in a review form before saving
- I can edit AI-generated content before committing it to my world
- Generated elements reference existing campaign data appropriately

**Technical Notes:**
- AI response parsing for structured data
- Draft forms for reviewing AI content
- Validation of generated data
- Integration with existing world elements

---

### Story 2.4: Batch Content Generation
**As a DM**, I want to ask the AI to generate multiple related elements at once, so that I can quickly populate areas of my world.

**Acceptance Criteria:**
- I can request multiple NPCs for a location (e.g., "5 NPCs for this tavern")
- I can generate sets of related plot hooks
- Batch-generated content maintains internal consistency
- Each generated element can be individually reviewed and edited

**Technical Notes:**
- Batch generation prompts
- Multiple element parsing from AI responses
- Individual review forms for each element
- Relationship suggestion between generated elements

---

## Epic 3: Ideas Management

### Story 3.1: Ideas Inbox
**As a DM**, I want to capture loose ideas and organize them by development status, so that I don't lose inspiration and can develop ideas over time.

**Acceptance Criteria:**
- I can quickly add raw ideas with minimal structure
- Ideas are categorized by type (NPC, location, etc.)
- Ideas have status tracking (raw → developing → ready → implemented)
- I can add notes and priority levels to ideas

**Technical Notes:**
- Simple idea capture interface
- Status workflow management
- Filtering and sorting by status, type, priority
- Connection to AI chat sessions

---

### Story 3.2: Idea Development Workflow
**As a DM**, I want to move ideas through a development process, so that I can systematically turn inspiration into usable campaign content.

**Acceptance Criteria:**
- I can change idea status as I develop them
- I can link ideas to AI chat sessions where they were discussed
- When implementing an idea, I can convert it to the appropriate world element
- Implemented ideas maintain a connection to their original inspiration

**Technical Notes:**
- Status transition validation
- Conversion workflow from idea to world element
- Bidirectional linking between ideas and implemented elements
- History tracking for idea development

---

## Epic 4: NPC Management

### Story 4.1: NPC Creation and Editing
**As a DM**, I want to create detailed NPCs with personality and background information, so that I can roleplay them consistently.

**Acceptance Criteria:**
- I can enter basic information (name, race, gender, age, occupation)
- I can add personality traits, ideals, bonds, and flaws
- I can write appearance and background descriptions
- I can set the NPC's current location
- I can upload an image for the NPC

**Technical Notes:**
- Comprehensive NPC form with validation
- Image upload and storage
- Location dropdown populated from campaign locations
- Rich text editing for descriptions

---

### Story 4.2: NPC Relationships
**As a DM**, I want to track relationships between NPCs, so that I can create a web of interconnected characters.

**Acceptance Criteria:**
- I can define relationships between NPCs (family, friends, enemies, etc.)
- Relationships are bidirectional and show on both NPCs
- I can see a visual representation of NPC connections
- I can add notes about the nature of each relationship

**Technical Notes:**
- Relationship management interface
- Bidirectional relationship creation
- Relationship visualization component
- Filtering relationships by type and strength

---

### Story 4.3: NPC Search and Organization
**As a DM**, I want to quickly find NPCs by various criteria, so that I can access the right character information during gameplay.

**Acceptance Criteria:**
- I can search NPCs by name, occupation, or location
- I can filter NPCs by status (active, historical, dead)
- I can sort NPCs by various fields (name, location, creation date)
- Search results highlight matching terms
- I can quickly navigate from search results to full NPC details

**Technical Notes:**
- Full-text search implementation
- Multi-field filtering interface
- Sorting controls with persistence
- Highlighting of search terms in results
- Pagination for large NPC lists

---

## Epic 5: Location Management

### Story 5.1: Location Hierarchy
**As a DM**, I want to organize locations in a hierarchical structure, so that I can represent regions, cities, and buildings in a logical way.

**Acceptance Criteria:**
- I can create parent-child relationships between locations
- I can see a tree view of location hierarchy
- Child locations inherit appropriate properties from parents
- I can move locations within the hierarchy
- Navigation shows location breadcrumbs

**Technical Notes:**
- Hierarchical data structure with parent_location_id
- Tree view component for navigation
- Breadcrumb navigation system
- Drag-and-drop for reorganizing hierarchy
- Inheritance rules for location properties

---

### Story 5.2: Settlement Details
**As a DM**, I want to track detailed information about settlements, so that they feel like real, lived-in places.

**Acceptance Criteria:**
- I can enter population and demographic information
- I can specify government type and economic status
- I can list notable features and current events
- I can track trade goods and connections to other locations
- I can upload maps and images for the location

**Technical Notes:**
- Specialized forms for different location types
- Demographic data structure (JSON fields)
- Trade goods management interface
- Connection mapping between locations
- Map image upload and display

---

### Story 5.3: Location-NPC Integration
**As a DM**, I want to see which NPCs are associated with each location, so that I can understand the social landscape of my world.

**Acceptance Criteria:**
- Location pages show all NPCs currently at that location
- I can quickly add NPCs to a location
- I can move NPCs between locations
- NPC pages show their current and past locations
- Location population counts reflect NPC assignments

**Technical Notes:**
- NPC-location relationship display
- Quick NPC assignment interface
- Location history tracking for NPCs
- Population calculation based on NPC assignments
- Bulk NPC movement tools

---

## Epic 6: Organization Management

### Story 6.1: Organization Creation
**As a DM**, I want to create organizations with goals and hierarchies, so that I can model political and social structures.

**Acceptance Criteria:**
- I can create organizations with type, scope, and basic information
- I can set headquarters locations and leader NPCs
- I can define organizational goals and methods
- I can track membership size and influence level
- I can upload organizational symbols and images

**Technical Notes:**
- Organization creation form with type-specific fields
- Leader and headquarters dropdowns from existing NPCs/locations
- Goals and methods as dynamic lists
- Influence and membership tracking
- Symbol/logo image upload

---

### Story 6.2: Organization Relationships
**As a DM**, I want to track relationships between organizations, so that I can model political alliances and conflicts.

**Acceptance Criteria:**
- I can define ally and enemy relationships between organizations
- I can see a network view of organizational relationships
- I can track how relationships change over time
- Relationship changes can trigger plot hooks or events

**Technical Notes:**
- Organization relationship management interface
- Network visualization for organizational politics
- Relationship history tracking
- Integration with plot hook and event systems
- Conflict and alliance detection

---

### Story 6.3: Organization Membership
**As a DM**, I want to track which NPCs belong to which organizations, so that I can understand loyalties and hierarchies.

**Acceptance Criteria:**
- I can assign NPCs to organizations with specific roles
- I can see organizational charts showing hierarchies
- I can track membership changes over time
- Organization pages show all current members
- NPC pages show all organizational affiliations

**Technical Notes:**
- NPC-organization membership system with roles
- Hierarchical organization chart visualization
- Membership history tracking
- Cross-referencing between NPCs and organizations
- Role-based permissions and influence modeling

---

## Epic 7: Plot Hook Management

### Story 7.1: Plot Hook Creation
**As a DM**, I want to create plot hooks that connect to existing world elements, so that story opportunities emerge naturally from my world.

**Acceptance Criteria:**
- I can create plot hooks with titles, descriptions, and types
- I can set urgency levels and complexity ratings
- I can link plot hooks to relevant NPCs, locations, and organizations
- I can define prerequisites and potential rewards
- I can outline success and failure consequences

**Technical Notes:**
- Plot hook creation form with relationship linking
- Multi-select interfaces for related elements
- Prerequisite definition system
- Reward and consequence tracking
- Plot hook categorization and prioritization

---

### Story 7.2: Plot Hook Status Tracking
**As a DM**, I want to track the progress of plot hooks through my campaign, so that I can manage ongoing storylines.

**Acceptance Criteria:**
- Plot hooks have status (draft, available, active, completed, failed, abandoned)
- I can update plot hook status as the campaign progresses
- I can see which plot hooks are currently active
- Completed plot hooks show their resolution
- Failed plot hooks can be modified and reactivated

**Technical Notes:**
- Plot hook status workflow management
- Status change tracking with timestamps
- Active plot hook dashboard
- Resolution tracking for completed hooks
- Plot hook reactivation system

---

### Story 7.3: Plot Hook Interconnections
**As a DM**, I want to see how plot hooks connect to each other, so that I can weave complex storylines.

**Acceptance Criteria:**
- I can see which plot hooks share NPCs, locations, or organizations
- I can create explicit connections between related plot hooks
- I can visualize plot hook networks and dependencies
- I can track how resolving one plot hook affects others

**Technical Notes:**
- Plot hook relationship detection based on shared elements
- Explicit plot hook linking system
- Network visualization for story connections
- Dependency tracking and cascade effects
- Story arc management tools

---

## Epic 8: Session Management

### Story 8.1: Session Note Taking
**As a DM**, I want to record what happens during each session, so that I can track campaign progress and maintain continuity.

**Acceptance Criteria:**
- I can create session notes with date and session number
- I can record major events and their outcomes
- I can track NPC interactions and relationship changes
- I can note locations visited and items gained/lost
- I can update plot hook progress within session notes

**Technical Notes:**
- Session note creation and editing interface
- Event tracking with categorization
- NPC interaction logging with relationship impacts
- Location and item transaction tracking
- Plot hook progress integration

---

### Story 8.2: World State Updates
**As a DM**, I want session events to automatically update relevant world elements, so that my world reflects what happened in the game.

**Acceptance Criteria:**
- NPC relationship changes in session notes update NPC records
- Location visits are tracked in location histories
- Item transactions update current owner/location
- Plot hook advancement updates plot hook status
- Character deaths or status changes are reflected in NPC records

**Technical Notes:**
- Automated world state updates from session notes
- Relationship change propagation system
- Location and item history tracking
- Plot hook status synchronization
- NPC status change management

---

## Epic 9: AI Integration Advanced Features

### Story 9.1: Consequence Prediction
**As a DM**, I want the AI to help me understand potential consequences of player actions, so that I can maintain a reactive world.

**Acceptance Criteria:**
- I can describe a player action and get predicted consequences
- AI considers existing world state when predicting outcomes
- Predictions include effects on NPCs, organizations, and locations
- AI suggests new plot hooks that might emerge from consequences
- Predictions help me prepare for different scenario outcomes

**Technical Notes:**
- Consequence prediction prompts with world context
- Impact analysis across different world elements
- Plot hook generation from predicted outcomes
- Scenario planning assistance
- World state impact modeling

---

### Story 9.2: Relationship Suggestions
**As a DM**, I want the AI to suggest connections between world elements, so that my world feels more interconnected.

**Acceptance Criteria:**
- AI analyzes existing world elements and suggests relationships
- Suggestions consider thematic consistency and logical connections
- I can accept, modify, or reject AI relationship suggestions
- AI explains the reasoning behind relationship suggestions
- Suggestions help fill gaps in world connectivity

**Technical Notes:**
- World element analysis for relationship opportunities
- Thematic and logical relationship algorithms
- Suggestion review and modification interface
- Reasoning explanation for AI suggestions
- Gap analysis in world connectivity

---

### Story 9.3: Dynamic Plot Generation
**As a DM**, I want the AI to suggest plot developments based on current world state, so that stories emerge organically from existing elements.

**Acceptance Criteria:**
- AI analyzes current world state and suggests emerging plots
- Suggestions consider NPC motivations and organizational goals
- AI identifies potential conflicts and opportunities
- Suggested plots build on existing relationships and tensions
- I can develop AI suggestions into full plot hooks

**Technical Notes:**
- World state analysis for plot opportunities
- Motivation and goal-based plot generation
- Conflict and opportunity identification
- Plot development assistance tools
- Integration with plot hook creation system

---

## Epic 10: File and Media Management

### Story 10.1: Image Upload and Management
**As a DM**, I want to upload and manage images for my world elements, so that I can visualize my campaign.

**Acceptance Criteria:**
- I can upload images for NPCs, locations, organizations, and items
- Images are properly resized and optimized for web display
- I can replace or remove images from world elements
- Image galleries show all images for a campaign
- Images are securely stored and served

**Technical Notes:**
- Multi-entity image upload system
- Image processing and optimization
- Image replacement and deletion functionality
- Gallery view for campaign images
- Secure file storage and serving

---

### Story 10.2: Image Organization
**As a DM**, I want to organize and categorize images, so that I can easily find the right visual content.

**Acceptance Criteria:**
- Images are automatically categorized by entity type
- I can add tags and descriptions to images
- I can search images by tags, descriptions, or associated elements
- I can create custom image collections or albums
- Unused images are identified for potential cleanup

**Technical Notes:**
- Automatic image categorization system
- Tagging and metadata management
- Image search functionality
- Custom collection creation and management
- Unused image detection and cleanup tools

---

## Epic 11: Search and Navigation

### Story 11.1: Global Campaign Search
**As a DM**, I want to search across all campaign content, so that I can quickly find any information during gameplay.

**Acceptance Criteria:**
- I can search across NPCs, locations, organizations, plot hooks, events, and items
- Search results show the type and context of each match
- Search supports partial matches and synonyms
- I can filter search results by element type
- Search is fast enough to use during active gameplay

**Technical Notes:**
- Full-text search across all campaign tables
- Search result aggregation and ranking
- Type-based filtering of search results
- Performance optimization for real-time use
- Synonym and partial match support

---

### Story 11.2: Quick Reference Tools
**As a DM**, I want quick access to frequently needed information, so that I can run sessions smoothly.

**Acceptance Criteria:**
- I can access a quick reference panel with recent/starred elements
- I can pin important NPCs or locations for easy access
- I can maintain a session-specific "active" elements list
- Quick reference shows condensed but essential information
- I can update element status directly from quick reference

**Technical Notes:**
- Quick reference sidebar or panel
- Element pinning and starring system
- Session-specific active element tracking
- Condensed element display formats
- Inline editing capabilities for quick updates

---

## Epic 12: Data Import/Export

### Story 12.1: Campaign Backup and Export
**As a DM**, I want to export my campaign data, so that I can backup my work and potentially share it with others.

**Acceptance Criteria:**
- I can export complete campaign data in multiple formats (JSON, PDF)
- Exports include all world elements and their relationships
- Exported data maintains referential integrity
- I can choose what to include/exclude from exports
- Export process handles large campaigns efficiently

**Technical Notes:**
- Multi-format export system (JSON, PDF)
- Complete data relationship preservation
- Selective export options
- Large dataset handling and streaming
- Export job management for complex campaigns

---

### Story 12.2: Campaign Import
**As a DM**, I want to import campaign data from other sources, so that I can migrate existing campaigns or use shared content.

**Acceptance Criteria:**
- I can import data from exported campaign files
- Import process validates data integrity and relationships
- I can preview import changes before committing
- Import handles conflicts with existing data gracefully
- I can selectively import specific elements

**Technical Notes:**
- Import file parsing and validation
- Data integrity checking and relationship rebuilding
- Import preview and confirmation system
- Conflict resolution strategies
- Selective import capabilities

---

## Epic 13: Performance and Polish

### Story 13.1: Mobile-Friendly Interface
**As a DM**, I want the toolkit to work well on mobile devices, so that I can access information during sessions away from my computer.

**Acceptance Criteria:**
- Interface adapts to mobile screen sizes
- Touch interactions work smoothly
- Mobile interface prioritizes most important information
- Search and quick reference work well on mobile
- Image viewing is optimized for mobile screens

**Technical Notes:**
- Responsive design implementation
- Touch-optimized UI components
- Mobile-first information hierarchy
- Optimized mobile search interface
- Mobile image viewing experience

---

### Story 13.2: Performance Optimization
**As a DM**, I want the application to load and respond quickly, so that it doesn't slow down my game sessions.

**Acceptance Criteria:**
- Pages load in under 2 seconds on standard connections
- Search results appear in under 500ms
- Image loading doesn't block other interface elements
- Large campaigns (500+ elements) maintain good performance
- AI responses stream to provide immediate feedback

**Technical Notes:**
- Performance monitoring and optimization
- Lazy loading for large datasets
- Image optimization and progressive loading
- Database query optimization and indexing
- AI response streaming implementation

---

## Testing User Stories

### Story T.1: End-to-End Campaign Creation
**As a QA tester**, I want to verify the complete campaign creation workflow, so that users can successfully build campaigns from start to finish.

**Test Scenario:**
1. Create new campaign with basic information
2. Use AI to generate initial NPCs and locations
3. Create relationships between generated elements
4. Add plot hooks connecting the elements
5. Run a mock session and update world state
6. Verify all data persists correctly and relationships are maintained

---

### Story T.2: AI Integration Testing
**As a QA tester**, I want to verify AI integration works correctly, so that users get consistent and helpful AI assistance.

**Test Scenario:**
1. Start AI chat session with empty campaign
2. Generate various types of content through conversation
3. Verify AI maintains context throughout session
4. Test batch generation of multiple elements
5. Verify generated content integrates properly with world data
6. Test AI error handling when service is unavailable

---

These user stories provide comprehensive coverage of the DM Toolkit functionality, from basic CRUD operations to advanced AI integration and performance requirements. Each story includes acceptance criteria that can guide development and testing, along with technical notes to help implementers understand the underlying requirements.