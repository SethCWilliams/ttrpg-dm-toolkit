import json
from typing import Dict, Any, Optional
from .service import ai_manager

class NPCGenerator:
    """NPC generation using AI services"""
    
    @staticmethod
    def _build_npc_prompt(campaign_context: Optional[Dict] = None, locked_fields: Optional[Dict] = None) -> str:
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
- AVOID using quotes within string values - use alternative descriptions
- For units of measurement, use words instead of symbols

Create a unique, memorable character that would fit well in a fantasy setting. Make them interesting with clear motivations, flaws, and potential for interesting interactions with player characters. Avoid generic stereotypes and give them personality depth.

CRITICAL: Ensure your response is complete and ends with a closing brace }."""

        # Add locked field constraints
        if locked_fields and any(locked_fields.values()):
            constraints_info = "\n\nIMPORTANT CONSTRAINTS - Use these EXACT values for the specified fields:\n"
            for field, value in locked_fields.items():
                if value:  # Only add non-empty constraints
                    constraints_info += f"- {field}: {value}\n"
            constraints_info += "\nGenerate the remaining fields to work well with these locked values. Make sure the character is cohesive and the unlocked fields complement the locked ones."
            base_prompt += constraints_info

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
        
        # Add race-appropriate height guidance
        base_prompt += """

HEIGHT GUIDANCE BY RACE:
- Dwarves: typically three to four feet tall
- Halflings: typically three to four feet tall  
- Gnomes: typically three to four feet tall
- Goblins: typically three to four feet tall
- Kobolds: typically two to three feet tall
- Goliaths: typically seven to eight feet tall
- Orcs: typically six to seven feet tall
- Half-Orcs: typically five to six feet tall
- Dragonborn: typically six to seven feet tall
- Tieflings: typically five to six feet tall
- Humans: typically five to six feet tall
- Elves: typically five to six feet tall
- Half-Elves: typically five to six feet tall

Choose an appropriate height for the character's race."""
        
        return base_prompt
    
    @staticmethod
    async def generate_npc(campaign_context: Optional[Dict] = None, locked_fields: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a complete NPC using AI"""
        
        try:
            prompt = NPCGenerator._build_npc_prompt(campaign_context, locked_fields)
            
            # Generate the NPC using AI
            response = await ai_manager.generate_text(
                prompt,
                temperature=0.8,  # Higher creativity
                max_tokens=1500   # Increased to ensure complete responses
            )
            
            # Parse JSON response
            try:
                print(f"Raw AI response: {response}")  # Show full response
                
                # Try to parse the raw response directly
                try:
                    # Clean up common JSON issues
                    cleaned_response = response.strip()
                    
                    import re
                    
                    # Fix age field if it has "years old" text
                    original_age = cleaned_response
                    cleaned_response = re.sub(r'"age":\s*"(\d+)\s+years?\s+old"', r'"age": \1', cleaned_response)
                    if original_age != cleaned_response:
                        print("FIXED: Removed 'years old' from age field")
                    
                    # Check if JSON ends with closing brace
                    if not cleaned_response.endswith('}'):
                        print(f"FIXING: Response doesn't end with }}. Adding closing brace.")
                        cleaned_response = cleaned_response.rstrip() + '}'
                    else:
                        print("✓ Response already ends with closing brace")
                    
                    # Count braces to ensure we have a complete JSON object
                    open_braces = cleaned_response.count('{')
                    close_braces = cleaned_response.count('}')
                    print(f"Braces count: {{ = {open_braces}, }} = {close_braces}")
                    
                    if open_braces > close_braces:
                        missing_braces = open_braces - close_braces
                        print(f"FIXING: Missing {missing_braces} closing braces. Adding them.")
                        cleaned_response += '}' * missing_braces
                    else:
                        print("✓ Brace count is balanced")
                    
                    print(f"Final cleaned response length: {len(cleaned_response)}")
                    print(f"Final ends with: ...{cleaned_response[-50:]}")
                    npc_data = json.loads(cleaned_response)
                except json.JSONDecodeError as e:
                    print(f"JSON parsing failed: {e}")
                    print(f"Full response: {response}")
                    raise e
                
                # Validate required fields and provide defaults if missing
                required_fields = {
                    'name': 'Unknown Traveler',
                    'race': 'Human',
                    'gender': 'Male',
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
            'gender': 'Male',
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