import json
from typing import Dict, Any, Optional
from ..service import ai_manager


class LocationGenerator:
    """Location generation using AI services"""
    
    @staticmethod
    def _build_location_prompt(location_type: str, campaign_context: Optional[Dict] = None, locked_fields: Optional[Dict] = None) -> str:
        """Build a comprehensive location generation prompt based on type"""
        
        # Base prompt varies by location type
        type_prompts = {
            'settlement': """You are a creative dungeon master creating a new settlement (city, town, or village) for a tabletop RPG campaign.""",
            'dungeon': """You are a creative dungeon master creating a new dungeon or underground complex for a tabletop RPG campaign.""",
            'wilderness': """You are a creative dungeon master creating a new wilderness area or natural location for a tabletop RPG campaign.""",
            'structure': """You are a creative dungeon master creating a new building or constructed location for a tabletop RPG campaign.""",
            'region': """You are a creative dungeon master creating a new region or large geographical area for a tabletop RPG campaign."""
        }
        
        base_prompt = type_prompts.get(location_type, type_prompts['settlement'])
        
        # Generate type-specific JSON structure based on actual form templates
        if location_type == 'settlement':
            json_structure = """{
    "name": "settlement name",
    "description": "detailed description of the settlement's appearance and atmosphere",
    "history": "background story and historical significance",
    "population": 500,
    "government_type": "leadership type - use EXACTLY one of: mayor, council, lord, elder, chieftain, guild_master, other",
    "economic_status": "economic condition - use EXACTLY one of: thriving, prosperous, stable, declining, poor",
    "defenses": "defensive capabilities and security measures",
    "notable_features": ["notable location 1", "notable location 2", "notable location 3"],
    "trade_goods": ["trade good 1", "trade good 2", "trade good 3"],
    "demographics": "description of who lives here and their composition"
}"""
        elif location_type == 'structure':
            json_structure = """{
    "name": "building name",
    "description": "detailed description of the building's appearance and atmosphere",
    "history": "background story and historical significance",
    "structure_type": "building type - use EXACTLY one of: inn, tavern, shop, temple, guild_hall, manor, castle, tower, warehouse, other",
    "owner": "owner or proprietor name and details",
    "notable_features": ["feature 1", "feature 2", "feature 3"],
    "services": ["service 1", "service 2", "service 3"],
    "security": "security measures and defenses",
    "ambient_description": "sounds, smells, and atmosphere that characters would notice"
}"""
        elif location_type == 'dungeon':
            json_structure = """{
    "name": "dungeon name",
    "description": "detailed description of the dungeon's appearance and atmosphere",
    "history": "background story and historical significance",
    "dungeon_type": "dungeon type - use EXACTLY one of: ruins, tomb, cave, mine, fortress, laboratory, temple, prison, other",
    "difficulty": "difficulty level - use EXACTLY one of: easy, moderate, hard, deadly",
    "defenses": "traps, defenses, and security measures",
    "notable_features": ["feature 1", "feature 2", "feature 3"],
    "treasures": "potential treasures and rewards",
    "ambient_description": "sounds, smells, and atmosphere that characters would notice"
}"""
        elif location_type == 'wilderness':
            json_structure = """{
    "name": "wilderness area name",
    "description": "detailed description of the natural area's appearance and atmosphere",
    "history": "background story and historical significance",
    "terrain_type": "terrain type - use EXACTLY one of: forest, mountains, plains, desert, swamp, coast, river, lake, hills, other",
    "climate": "weather and climate conditions",
    "dangers": ["natural hazard 1", "threat 2", "danger 3"],
    "notable_features": ["landmark 1", "point of interest 2", "feature 3"],
    "wildlife": ["creature 1", "animal 2", "species 3"],
    "resources": ["resource 1", "resource 2", "resource 3"],
    "ambient_description": "sounds, smells, and atmosphere that characters would notice"
}"""
        elif location_type == 'region':
            json_structure = """{
    "name": "region name",
    "description": "detailed description of the region's geography and atmosphere",
    "history": "background story and historical significance",
    "government_type": "government type - use EXACTLY one of: kingdom, empire, republic, city_state, tribal, theocracy, anarchy, other",
    "population": 50000,
    "economic_status": "economic condition - use EXACTLY one of: prosperous, stable, struggling, impoverished, wealthy",
    "notable_features": ["geographical feature 1", "landmark 2", "feature 3"],
    "climate": "climate and weather patterns",
    "natural_resources": ["resource 1", "resource 2", "resource 3"]
}"""
        else:
            # Fallback to settlement structure
            json_structure = """{{
    "name": "location name",
    "type": "{location_type}",
    "description": "detailed description",
    "history": "background story",
    "notable_features": ["feature 1", "feature 2"]
}}"""

        base_prompt += f" Generate a detailed, interesting {location_type} with the following information. Return the response as valid JSON with exactly these fields:\n\n{json_structure}\n\n"

        base_prompt += """IMPORTANT: 
- Arrays should contain 2-4 relevant items (notable_features, services, resources, etc.)
- Text fields like ambient_description, security, owner should be STRINGS not arrays
- Use appropriate values for the location type
- Ensure all JSON arrays are properly closed with ]
- Ensure all JSON objects are properly closed with }}
- Use proper JSON syntax with double quotes around all strings
- AVOID using quotes within string values - use alternative descriptions
- Return ONLY the JSON, no additional text

FANTASY SETTING REQUIREMENTS:
- This is a HIGH FANTASY world with magic, wizards, clerics, and fantasy races
- Use fantasy-appropriate names (avoid real-world cultural references like Ottoman, Arabian, etc.)
- Consider magical elements: enchanted items, spell components, magical services
- Fantasy races may be present: humans, elves, dwarves, halflings, gnomes, etc.
- Include fantasy elements: magical lighting, enchantments, alchemy, divine blessing
- Use generic fantasy naming conventions rather than specific real-world cultures
- Think D&D, Lord of the Rings, or generic fantasy rather than historical periods"""

        # Add type-specific guidance
        if location_type == 'settlement':
            base_prompt += """

SETTLEMENT-SPECIFIC GUIDANCE:
- Population should be realistic (hamlet: 50-100, village: 100-1000, town: 1000-5000, city: 5000+)
- Include appropriate government for size (elder council, mayor, lord, etc.)
- Consider defensive walls, guards, militia based on size and threat level
- Trade goods should reflect local resources and crafts"""
        
        elif location_type == 'dungeon':
            base_prompt += """

DUNGEON-SPECIFIC GUIDANCE:
- Population refers to current inhabitants (monsters, cultists, etc.)
- Government_type refers to hierarchy among inhabitants
- Economic_status refers to treasure and resources present
- Notable_features should include traps, puzzles, or unique rooms
- Consider the dungeon's original purpose and current state"""
        
        elif location_type == 'wilderness':
            base_prompt += """

WILDERNESS-SPECIFIC GUIDANCE:
- Population refers to wildlife and any inhabitants
- Government_type could be "natural order" or territorial creatures
- Economic_status refers to available resources and dangers
- Notable_features should include terrain, landmarks, and natural hazards
- Consider seasonal variations and weather patterns"""
        
        elif location_type == 'structure':
            base_prompt += """

STRUCTURE-SPECIFIC GUIDANCE:
- Population refers to occupants or capacity
- Government_type refers to management or ownership
- Economic_status refers to the building's wealth or purpose
- Notable_features should include architectural details and special rooms
- Consider the structure's purpose and current condition
- For taverns/inns: Include fantasy elements like magical warming, enchanted kegs, rooms warded against scrying
- For shops: Consider what magical items, spell components, or fantasy goods they might sell
- For temples: Dedicated to fantasy deities, may have clerical magic or divine blessings
- Use fantasy architectural elements: stone construction, wooden beams, magical lighting"""
        
        elif location_type == 'region':
            base_prompt += """

REGION-SPECIFIC GUIDANCE:
- Population should be the total across all settlements
- Government_type refers to regional authority or political structure
- Economic_status reflects the overall wealth and trade
- Notable_features should include major landmarks and geographical features
- Consider climate, terrain, and major settlements within"""

        # Add locked field constraints
        if locked_fields and any(locked_fields.values()):
            constraints_info = "\n\nIMPORTANT CONSTRAINTS - Use these EXACT values for the specified fields:\n"
            for field, value in locked_fields.items():
                if value:  # Only add non-empty constraints
                    constraints_info += f"- {field}: {value}\n"
            constraints_info += "\nGenerate the remaining fields to work well with these locked values. Make sure the location is cohesive and the unlocked fields complement the locked ones."
            base_prompt += constraints_info

        # Add campaign context if provided
        if campaign_context:
            context_info = f"\n\nCampaign Context:\n"
            if campaign_context.get('world_name'):
                context_info += f"- World: {campaign_context['world_name']}\n"
            if campaign_context.get('campaign_name'):
                context_info += f"- Campaign: {campaign_context['campaign_name']}\n"
            if campaign_context.get('existing_locations'):
                context_info += f"- Known Locations: {', '.join(campaign_context['existing_locations'])}\n"
            if campaign_context.get('theme'):
                context_info += f"- Campaign Theme: {campaign_context['theme']}\n"
            
            base_prompt += context_info + "\nConsider this context when creating the location, but don't feel restricted by it."
        
        base_prompt += "\n\nIMPORTANT: Return ONLY valid JSON, no additional text or formatting."
        base_prompt += "\n\nCreate a unique, memorable location that would fit well in a fantasy setting. Make it interesting with clear purpose, history, and potential for adventures."
        
        return base_prompt
    
    @staticmethod
    async def generate_location(location_type: str, campaign_context: Optional[Dict] = None, locked_fields: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a complete location using AI"""
        
        try:
            prompt = LocationGenerator._build_location_prompt(location_type, campaign_context, locked_fields)
            
            # Generate the location using AI
            response = await ai_manager.generate_text(
                prompt,
                temperature=0.8,  # Higher creativity
                max_tokens=1500   # Increased to ensure complete responses
            )
            
            # Parse JSON response
            try:
                print(f"Raw AI response: {response}")  # Show full response
                
                # Clean up common JSON issues
                cleaned_response = response.strip()
                
                # Find the JSON object - look for the first { and take everything from there
                start_idx = cleaned_response.find('{')
                if start_idx > 0:
                    cleaned_response = cleaned_response[start_idx:]
                
                import re
                
                # Fix population field - extract only the numeric value
                cleaned_response = re.sub(r'"population":\s*"([^"]*?(\d+)[^"]*?)"', r'"population": \2', cleaned_response)
                
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
                location_data = json.loads(cleaned_response)
                
                # Debug: Check what type the notable_features field is after JSON parsing
                if 'notable_features' in location_data:
                    print(f"notable_features type: {type(location_data['notable_features'])}")
                    print(f"notable_features value: {location_data['notable_features']}")
                if 'services' in location_data:
                    print(f"services type: {type(location_data['services'])}")
                    print(f"services value: {location_data['services']}")
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                print(f"Full response: {response}")
                raise e
            
            # Ensure basic fields exist
            location_data['name'] = location_data.get('name', 'Unnamed Location')
            location_data['type'] = location_type
            location_data['description'] = location_data.get('description', 'A mysterious location waiting to be explored')
            location_data['history'] = location_data.get('history', 'This location has ancient origins')
            
            # Keep arrays as arrays for tags fields - don't convert to strings
            # The frontend expects arrays for tags fields like notable_features, services, etc.
            array_fields = ['notable_features', 'services', 'trade_goods', 'resources', 'natural_resources', 'dangers', 'wildlife']
            for field in array_fields:
                if field in location_data:
                    if isinstance(location_data[field], list):
                        # Clean up the array items but keep as array
                        valid_items = []
                        for item in location_data[field]:
                            if item and str(item).strip():  # Only include non-empty items
                                valid_items.append(str(item).strip())
                        location_data[field] = valid_items
                        print(f"Kept array {field}: {len(valid_items)} items")  # Debug output
                    elif isinstance(location_data[field], str):
                        # If it's a string, split it into array items
                        location_data[field] = [item.strip() for item in location_data[field].split(',') if item.strip()]
            
            # Ensure ambient_description is always a string, not an array
            if 'ambient_description' in location_data and isinstance(location_data['ambient_description'], list):
                location_data['ambient_description'] = '. '.join(str(item).strip() for item in location_data['ambient_description'] if item)
            
            # Clean up select field values to match allowed options
            if location_type == 'settlement':
                if 'government_type' in location_data:
                    gov_type = location_data['government_type'].lower()
                    if 'elder' in gov_type:
                        location_data['government_type'] = 'elder'
                    elif 'council' in gov_type:
                        location_data['government_type'] = 'council'
                    elif 'mayor' in gov_type:
                        location_data['government_type'] = 'mayor'
                    elif 'lord' in gov_type:
                        location_data['government_type'] = 'lord'
                    elif 'chief' in gov_type:
                        location_data['government_type'] = 'chieftain'
                    elif 'guild' in gov_type:
                        location_data['government_type'] = 'guild_master'
                    else:
                        location_data['government_type'] = 'other'
                        
                if 'economic_status' in location_data:
                    eco_status = location_data['economic_status'].lower()
                    if 'prosper' in eco_status or 'wealthy' in eco_status:
                        location_data['economic_status'] = 'prosperous'
                    elif 'thriv' in eco_status:
                        location_data['economic_status'] = 'thriving'  
                    elif 'stable' in eco_status:
                        location_data['economic_status'] = 'stable'
                    elif 'declin' in eco_status or 'strug' in eco_status:
                        location_data['economic_status'] = 'declining'
                    elif 'poor' in eco_status or 'impover' in eco_status:
                        location_data['economic_status'] = 'poor'
                    else:
                        location_data['economic_status'] = 'stable'
            
            elif location_type == 'region':
                if 'government_type' in location_data:
                    gov_type = location_data['government_type'].lower()
                    if 'kingdom' in gov_type:
                        location_data['government_type'] = 'kingdom'
                    elif 'empire' in gov_type:
                        location_data['government_type'] = 'empire'
                    elif 'republic' in gov_type:
                        location_data['government_type'] = 'republic'
                    elif 'city_state' in gov_type or 'city state' in gov_type:
                        location_data['government_type'] = 'city_state'
                    elif 'tribal' in gov_type or 'tribe' in gov_type:
                        location_data['government_type'] = 'tribal'
                    elif 'theocracy' in gov_type or 'religious' in gov_type:
                        location_data['government_type'] = 'theocracy'
                    elif 'anarchy' in gov_type or 'anarchist' in gov_type:
                        location_data['government_type'] = 'anarchy'
                    else:
                        location_data['government_type'] = 'other'
                        
                if 'economic_status' in location_data:
                    eco_status = location_data['economic_status'].lower()
                    if 'prosper' in eco_status:
                        location_data['economic_status'] = 'prosperous'
                    elif 'stable' in eco_status:
                        location_data['economic_status'] = 'stable'
                    elif 'strug' in eco_status:
                        location_data['economic_status'] = 'struggling'
                    elif 'impover' in eco_status or 'poor' in eco_status:
                        location_data['economic_status'] = 'impoverished'
                    elif 'wealthy' in eco_status:
                        location_data['economic_status'] = 'wealthy'
                    else:
                        location_data['economic_status'] = 'stable'
            
            elif location_type == 'dungeon':
                if 'dungeon_type' in location_data:
                    dungeon_type = location_data['dungeon_type'].lower()
                    if 'ruin' in dungeon_type:
                        location_data['dungeon_type'] = 'ruins'
                    elif 'tomb' in dungeon_type or 'crypt' in dungeon_type or 'mausoleum' in dungeon_type:
                        location_data['dungeon_type'] = 'tomb'
                    elif 'cave' in dungeon_type or 'cavern' in dungeon_type:
                        location_data['dungeon_type'] = 'cave'
                    elif 'mine' in dungeon_type or 'quarry' in dungeon_type:
                        location_data['dungeon_type'] = 'mine'
                    elif 'fortress' in dungeon_type or 'castle' in dungeon_type or 'stronghold' in dungeon_type:
                        location_data['dungeon_type'] = 'fortress'
                    elif 'laboratory' in dungeon_type or 'lab' in dungeon_type or 'workshop' in dungeon_type:
                        location_data['dungeon_type'] = 'laboratory'
                    elif 'temple' in dungeon_type or 'shrine' in dungeon_type or 'sanctuary' in dungeon_type:
                        location_data['dungeon_type'] = 'temple'
                    elif 'prison' in dungeon_type or 'jail' in dungeon_type or 'dungeon' in dungeon_type:
                        location_data['dungeon_type'] = 'prison'
                    else:
                        location_data['dungeon_type'] = 'other'
                        
                if 'difficulty' in location_data:
                    difficulty = location_data['difficulty'].lower()
                    if 'easy' in difficulty or 'simple' in difficulty or 'beginner' in difficulty:
                        location_data['difficulty'] = 'easy'
                    elif 'moderate' in difficulty or 'medium' in difficulty or 'average' in difficulty:
                        location_data['difficulty'] = 'moderate'
                    elif 'hard' in difficulty or 'difficult' in difficulty or 'challenging' in difficulty:
                        location_data['difficulty'] = 'hard'
                    elif 'deadly' in difficulty or 'lethal' in difficulty or 'extreme' in difficulty:
                        location_data['difficulty'] = 'deadly'
                    else:
                        location_data['difficulty'] = 'moderate'
            
            elif location_type == 'structure':
                if 'structure_type' in location_data:
                    struct_type = location_data['structure_type'].lower()
                    if 'inn' in struct_type:
                        location_data['structure_type'] = 'inn'
                    elif 'tavern' in struct_type:
                        location_data['structure_type'] = 'tavern'
                    elif 'shop' in struct_type or 'store' in struct_type:
                        location_data['structure_type'] = 'shop'
                    elif 'temple' in struct_type or 'shrine' in struct_type:
                        location_data['structure_type'] = 'temple'
                    elif 'guild' in struct_type:
                        location_data['structure_type'] = 'guild_hall'
                    elif 'manor' in struct_type or 'estate' in struct_type:
                        location_data['structure_type'] = 'manor'
                    elif 'castle' in struct_type or 'keep' in struct_type:
                        location_data['structure_type'] = 'castle'
                    elif 'tower' in struct_type or 'spire' in struct_type:
                        location_data['structure_type'] = 'tower'
                    elif 'warehouse' in struct_type or 'storage' in struct_type:
                        location_data['structure_type'] = 'warehouse'
                    else:
                        location_data['structure_type'] = 'other'
            
            elif location_type == 'wilderness':
                if 'terrain_type' in location_data:
                    terrain = location_data['terrain_type'].lower()
                    if 'forest' in terrain or 'wood' in terrain:
                        location_data['terrain_type'] = 'forest'
                    elif 'mountain' in terrain or 'peak' in terrain:
                        location_data['terrain_type'] = 'mountains'
                    elif 'plain' in terrain or 'grassland' in terrain:
                        location_data['terrain_type'] = 'plains'
                    elif 'desert' in terrain or 'sand' in terrain:
                        location_data['terrain_type'] = 'desert'
                    elif 'swamp' in terrain or 'marsh' in terrain:
                        location_data['terrain_type'] = 'swamp'
                    elif 'coast' in terrain or 'shore' in terrain or 'beach' in terrain:
                        location_data['terrain_type'] = 'coast'
                    elif 'river' in terrain or 'stream' in terrain:
                        location_data['terrain_type'] = 'river'
                    elif 'lake' in terrain or 'pond' in terrain:
                        location_data['terrain_type'] = 'lake'
                    elif 'hill' in terrain:
                        location_data['terrain_type'] = 'hills'
                    else:
                        location_data['terrain_type'] = 'other'
            
            return location_data
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, create a fallback location
            print(f"JSON parsing failed: {e}")
            print(f"Full response: {response}")
            return LocationGenerator._create_fallback_location(location_type)
        
        except Exception as e:
            print(f"Location generation failed: {e}")
            return LocationGenerator._create_fallback_location(location_type)
    
    @staticmethod
    def _create_fallback_location(location_type: str) -> Dict[str, Any]:
        """Create a fallback location when AI generation fails"""
        
        fallbacks = {
            'settlement': {
                'name': 'Millhaven',
                'description': 'A modest farming community built around an old water mill. Stone cottages line cobblestone streets, and fields of grain stretch beyond the village borders.',
                'population': 350,
                'demographics': 'Primarily human farmers and crafters with a few halfling families',
                'government_type': 'Village Council led by elected Mayor',
                'economic_status': 'Modest farming community with steady grain trade',
                'notable_features': 'Ancient stone mill wheel, Weekly market square, Old shrine to harvest deity',
                'current_events': 'Preparing for harvest festival, Recent reports of strange lights in nearby woods',
                'defenses': 'Village militia, Wooden palisade around central area',
                'trade_goods': 'Grain, Flour, Simple crafts, Preserved foods',
                'connected_locations': 'Main road connects to regional capital, Forest path leads to ancient ruins',
                'ambient_description': 'The sound of the turning mill wheel, smell of fresh bread, and distant lowing of cattle',
                'notes': 'Peaceful village perfect for starting adventures or as a safe haven. The old mill may hide secrets.'
            }
        }
        
        fallback = fallbacks.get(location_type, fallbacks['settlement']).copy()
        fallback['type'] = location_type
        fallback['history'] = f'This {location_type} has served the region for generations, though its true origins remain shrouded in mystery.'
        
        return fallback