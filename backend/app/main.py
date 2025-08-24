from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.auth import router as auth_router
from app.campaigns import router as campaigns_router
from app.npcs import router as npcs_router
from app.locations import router as locations_router
from app.organizations import router as organizations_router
from app.plot_hooks import router as plot_hooks_router
from app.items import router as items_router
from app.events import router as events_router
from app.ideas_inbox import router as ideas_router
from app.session_notes import router as session_notes_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DM Toolkit API",
    description="A comprehensive dungeon master toolkit API",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/auth", tags=["authentication"])
app.include_router(campaigns_router.router, prefix="/campaigns", tags=["campaigns"])
app.include_router(npcs_router.router, prefix="/campaigns/{campaign_id}/npcs", tags=["npcs"])
app.include_router(locations_router.router, prefix="/campaigns/{campaign_id}/locations", tags=["locations"])
app.include_router(organizations_router.router, prefix="/campaigns/{campaign_id}/organizations", tags=["organizations"])
app.include_router(plot_hooks_router.router, prefix="/campaigns/{campaign_id}/plot-hooks", tags=["plot-hooks"])
app.include_router(items_router.router, prefix="/campaigns/{campaign_id}/items", tags=["items"])
app.include_router(events_router.router, prefix="/campaigns/{campaign_id}/events", tags=["events"])
app.include_router(ideas_router.router, prefix="/campaigns/{campaign_id}/ideas", tags=["ideas"])
app.include_router(session_notes_router.router, prefix="/campaigns/{campaign_id}/sessions", tags=["session-notes"])

@app.get("/")
async def root():
    return {"message": "DM Toolkit API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}