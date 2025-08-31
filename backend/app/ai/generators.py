"""
Main entry point for AI content generators.

This module serves as the primary interface for all AI content generation functionality.
It imports and exposes all available generators in a convenient location.

Available Generators:
- LocationGenerator: Generate detailed locations of various types (settlements, dungeons, etc.)
- NPCGenerator: Generate non-player characters with rich backstories and personalities

Usage:
    from app.ai.generators import LocationGenerator, NPCGenerator
    
    # Generate content using the specialized generators
    location_data = await LocationGenerator.generate_location(location_type, context, locked_fields)
    npc_data = await NPCGenerator.generate_npc(context, locked_fields)

Architecture:
Each generator is organized in its own module within the generators/ package, allowing for:
- Clear separation of concerns
- Easy maintenance and testing
- Extensible architecture for future content types
"""

# Import all available generators from the generators package
from .generators.location_generator import LocationGenerator
from .generators.npc_generator import NPCGenerator

# Export the generators for easy access
__all__ = ['LocationGenerator', 'NPCGenerator']