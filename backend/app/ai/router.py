from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models import Campaign, User
from app.auth.router import get_current_user
from .generators import NPCGenerator
from .service import ai_manager

class GenerateNPCRequest(BaseModel):
    locked_fields: Optional[Dict[str, Any]] = {}

router = APIRouter()

@router.get("/status")
async def get_ai_status():
    """Get the status of available AI providers"""
    try:
        available_providers = ai_manager.get_available_providers()
        return {
            "available": len(available_providers) > 0,
            "providers": [provider.value for provider in available_providers]
        }
    except Exception as e:
        return {
            "available": False,
            "providers": [],
            "error": str(e)
        }

@router.post("/generate/npc/{campaign_id}")
async def generate_npc(
    campaign_id: int,
    request: GenerateNPCRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate an NPC using AI for a specific campaign"""
    
    # Verify campaign ownership
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Build campaign context for AI generation
        campaign_context = {
            'world_name': campaign.world_name,
            'campaign_name': campaign.name,
            'description': campaign.description
        }
        
        # TODO: In the future, add existing locations, NPCs, etc. for campaign awareness
        # existing_locations = db.query(Location).filter(Location.campaign_id == campaign_id).all()
        # campaign_context['existing_locations'] = [loc.name for loc in existing_locations]
        
        # Generate the NPC with locked field constraints
        npc_data = await NPCGenerator.generate_npc(campaign_context, request.locked_fields)
        
        return {
            "success": True,
            "npc": npc_data,
            "message": "NPC generated successfully"
        }
        
    except Exception as e:
        # Log the error and return a fallback response
        print(f"NPC generation error: {str(e)}")
        
        # Return fallback NPC
        fallback_npc = NPCGenerator._create_fallback_npc()
        
        return {
            "success": True,
            "npc": fallback_npc,
            "message": "NPC generated using fallback (AI service unavailable)",
            "warning": "AI generation failed, using predefined template"
        }

@router.post("/update-keys")
async def update_ai_keys(
    keys: Dict[str, str],
    current_user: User = Depends(get_current_user)
):
    """Update AI service API keys for the current user session"""
    try:
        openai_key = keys.get("openai_api_key")
        anthropic_key = keys.get("anthropic_api_key")
        
        ai_manager.update_api_keys(openai_key, anthropic_key)
        
        available_providers = ai_manager.get_available_providers()
        
        return {
            "success": True,
            "message": "API keys updated successfully",
            "available_providers": [provider.value for provider in available_providers]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update API keys: {str(e)}"
        )