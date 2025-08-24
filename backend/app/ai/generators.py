import json
from typing import Dict, Any, Optional
from .service import ai_manager

class NPCGenerator:
    """NPC generation using AI services"""
    
    @staticmethod
    def _build_npc_prompt(campaign_context: Optional[Dict] = None) -> str:
        """Build a comprehensive NPC generation prompt"""
        
        base_prompt = """You are a creative dungeon master creating a new NPC for a tabletop RPG campaign. Generate a detailed, interesting NPC with the following information. Return the response as valid JSON with exactly these fields:

{
    "name": "full character name",
    "race": "character race (e.g., Human, Elf, Dwarf, Halfling, etc.)",
    "gender": "Male/Female/Non-binary",
    "age": "age in years as a number",
    "occupation": "character's job or role",
    "location": "where they can typically be found",
    "personality_traits": ["trait 1", "trait 2", "trait 3"],
    "ideals": "what drives and motivates this character",
    "bonds": "important relationships or connections (as a simple string, not an array)",
    "flaws": "character weakness or negative trait",
    "background": "brief backstory and history",
    "appearance": "physical description",
    "voice_mannerisms": "how they speak or notable speech patterns",
    "secrets": "hidden information about the character",
    "plot_hooks": ["potential story hook 1", "potential story hook 2"],
    "notable_possessions": ["item 1", "item 2"],
    "relationships": "connections to other people or organizations (as a simple string, not an array)",
    "goals": "what the character wants to achieve",
    "fears": "what the character is afraid of",
    "notes": "additional DM notes and roleplay tips"
}

IMPORTANT: 
- Only personality_traits, plot_hooks, and notable_possessions should be arrays
- bonds, relationships, and all other fields should be simple strings
- Ensure all JSON arrays are properly closed with ]
- Ensure all JSON objects are properly closed with }
- Use proper JSON syntax with double quotes around all strings
- AVOID using quotes within string values - use alternative descriptions (e.g., "5 feet 8 inches tall" instead of "5'8"")
- For measurements, use words instead of symbols (e.g., "five feet eight inches" or "5 feet 8 inches")

Create a unique, memorable character that would fit well in a fantasy setting. Make them interesting with clear motivations, flaws, and potential for interesting interactions with player characters. Avoid generic stereotypes and give them personality depth."""

        # Add campaign context if provided
        if campaign_context:
            context_info = f"\n\nCampaign Context:\n"
            if campaign_context.get('world_name'):
                context_info += f"- World: {campaign_context['world_name']}\n"
            if campaign_context.get('existing_locations'):
                context_info += f"- Known Locations: {', '.join(campaign_context['existing_locations'])}\n"
            if campaign_context.get('theme'):
                context_info += f"- Campaign Theme: {campaign_context['theme']}\n"
            
            base_prompt += context_info + "\nConsider this context when creating the NPC, but don't feel restricted by it."
        
        base_prompt += "\n\nIMPORTANT: Return ONLY valid JSON, no additional text or formatting."
        
        return base_prompt
    
    @staticmethod
    async def generate_npc(campaign_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a complete NPC using AI"""
        
        try:
            prompt = NPCGenerator._build_npc_prompt(campaign_context)
            
            # Generate the NPC using AI
            response = await ai_manager.generate_text(
                prompt,
                temperature=0.8,  # Higher creativity
                max_tokens=1000   # Reduced to avoid truncation
            )
            
            # Parse JSON response
            try:
                print(f"Raw AI response: {response}")  # Show full response
                
                # Try to parse the raw response directly
                try:
                    # Ensure the JSON ends with a closing brace
                    cleaned_response = response.strip()
                    if not cleaned_response.endswith('}'):
                        cleaned_response = cleaned_response.rstrip() + '}'
                    
                    npc_data = json.loads(cleaned_response)
                except json.JSONDecodeError as e:
                    print(f"JSON parsing failed: {e}")
                    print(f"Full response: {response}")
                    raise e
                
                # Validate required fields and provide defaults if missing
                required_fields = {
                    'name': 'Unknown Traveler',
                    'race': 'Human',
                    'gender': 'Non-binary',
                    'age': 30,
                    'occupation': 'Wanderer',
                    'location': 'The local tavern',
                    'personality_traits': ['Curious', 'Cautious'],
                    'ideals': 'Freedom and adventure',
                    'bonds': 'Family back home',
                    'flaws': 'Too trusting of strangers',
                    'background': 'A simple traveler with unknown origins',
                    'appearance': 'Average height with weathered clothing',
                    'voice_mannerisms': 'Speaks softly with thoughtful pauses',
                    'secrets': 'Hiding their true identity',
                    'plot_hooks': ['Seeks help with a personal quest'],
                    'notable_possessions': ['A worn leather journal'],
                    'relationships': 'Distant from most people',
                    'goals': 'Find a place to belong',
                    'fears': 'Being discovered',
                    'notes': 'Can be used as a quest giver or helpful contact'
                }
                
                # Ensure all required fields exist
                for field, default_value in required_fields.items():
                    if field not in npc_data or not npc_data[field]:
                        npc_data[field] = default_value
                
                # Convert personality_traits to comma-separated string for the form
                if isinstance(npc_data.get('personality_traits'), list):
                    npc_data['personality_traits'] = ', '.join(npc_data['personality_traits'])
                
                # Convert plot_hooks to comma-separated string
                if isinstance(npc_data.get('plot_hooks'), list):
                    npc_data['plot_hooks'] = ', '.join(npc_data['plot_hooks'])
                
                # Convert notable_possessions to comma-separated string
                if isinstance(npc_data.get('notable_possessions'), list):
                    npc_data['notable_possessions'] = ', '.join(npc_data['notable_possessions'])
                
                return npc_data
                
            except json.JSONDecodeError as e:
                # If JSON parsing fails, create a fallback NPC
                print(f"JSON parsing failed: {e}")
                print(f"Full response: {response}")
                return NPCGenerator._create_fallback_npc()
            
        except Exception as e:
            print(f"NPC generation failed: {e}")
            return NPCGenerator._create_fallback_npc()
    
    @staticmethod
    def _create_fallback_npc() -> Dict[str, Any]:
        """Create a fallback NPC when AI generation fails"""
        return {
            'name': 'Mysterious Stranger',
            'race': 'Human',
            'gender': 'Non-binary',
            'age': 35,
            'occupation': 'Merchant',
            'location': 'The crossroads tavern',
            'personality_traits': 'Observant, Secretive, Well-traveled',
            'ideals': 'Knowledge is the greatest treasure',
            'bonds': 'Owes a debt to a powerful organization',
            'flaws': 'Cannot resist a good mystery',
            'background': 'Once served as a scout for a merchant guild, now travels alone gathering information and rare goods.',
            'appearance': 'Medium height with keen eyes and practical traveling clothes. Always carries a worn leather satchel.',
            'voice_mannerisms': 'Speaks in measured tones, often pausing to consider their words carefully',
            'secrets': 'Carries a map to a hidden treasure, but the location is cursed',
            'plot_hooks': 'Needs help retrieving a stolen artifact, Offers information in exchange for a favor',
            'notable_possessions': 'Ancient compass, Coded journal, Silver amulet',
            'relationships': 'Former colleague turned rival, Contact in the thieves guild',
            'goals': 'Uncover the truth about an ancient conspiracy',
            'fears': 'Being tracked down by former employers',
            'notes': 'Can serve as an information broker or quest giver. Has connections throughout the region.'
        }