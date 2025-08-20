# DM Toolkit

A comprehensive dungeon master toolkit that combines world-building, campaign management, and AI-assisted content creation. Built to help DMs create rich, lived-in worlds with unprecedented ease and depth.

## Features

- **Campaign Management**: Create and manage multiple campaigns with detailed statistics
- **World Building**: Comprehensive tools for NPCs, locations, organizations, plot hooks, events, and items
- **AI Integration**: Intelligent content generation and brainstorming assistance (coming soon)
- **Session Management**: Track gameplay sessions and maintain world continuity
- **Ideas Inbox**: Capture and develop creative ideas from brainstorming to implementation

## Technology Stack

- **Backend**: FastAPI with SQLAlchemy ORM and SQLite database
- **Frontend**: SvelteKit with TailwindCSS
- **Authentication**: JWT-based authentication system
- **Database**: SQLite for development, PostgreSQL ready for production

## Getting Started

### Prerequisites

- Python 3.11+ 
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
python run.py
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

## Usage

1. Visit `http://localhost:5173` in your browser
2. Create a new account or log in
3. Create your first campaign
4. Start building your world with NPCs, locations, and more!

## Project Structure

```
ttrpg_dm_app/
├── backend/
│   ├── app/
│   │   ├── auth/          # Authentication endpoints and utilities
│   │   ├── campaigns/     # Campaign management endpoints
│   │   ├── models.py      # Database models
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── database.py    # Database configuration
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── run.py            # Development server
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/  # Reusable Svelte components
│   │   │   └── stores/      # Svelte stores for state management
│   │   └── routes/          # SvelteKit routes
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Vite configuration
└── docs/                  # Project documentation
```

## Development

### Database Schema

The application uses a comprehensive database schema supporting:

- Users and authentication
- Campaigns with full statistics
- NPCs with relationships and detailed attributes
- Locations with hierarchical organization
- Organizations with membership and politics
- Plot hooks with prerequisites and consequences
- Events with causes and effects
- Items with mechanical properties
- Ideas inbox for brainstorming management

### API Design

The API follows RESTful principles with:

- JWT-based authentication
- Proper HTTP status codes
- Comprehensive error handling
- Automatic OpenAPI documentation
- Request/response validation with Pydantic

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Complete NPC management system
- [ ] Location hierarchy and connections
- [ ] Organization and political systems
- [ ] Plot hook tracking and relationships
- [ ] AI integration for content generation
- [ ] Session notes and world state tracking
- [ ] Image upload and management
- [ ] Import/export functionality
- [ ] Advanced search and filtering
- [ ] Mobile-responsive design improvements