"""
AI content generators for various game elements.

This package contains specialized generators for different types of content:
- LocationGenerator: Generate locations (settlements, dungeons, wilderness areas, etc.)
- NPCGenerator: Generate non-player characters with detailed personalities and backgrounds

Each generator follows a consistent pattern:
1. Build type-specific prompts with constraints and context
2. Generate content using AI services
3. Parse and validate the response
4. Return structured data ready for the frontend

Usage:
    from app.ai.generators import LocationGenerator, NPCGenerator
    
    # Generate a settlement
    location = await LocationGenerator.generate_location('settlement', context, locked_fields)
    
    # Generate an NPC
    npc = await NPCGenerator.generate_npc(context, locked_fields)
"""

from .location_generator import LocationGenerator
from .npc_generator import NPCGenerator

__all__ = ['LocationGenerator', 'NPCGenerator']