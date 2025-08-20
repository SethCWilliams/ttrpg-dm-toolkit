# DM Toolkit - Examples Document

## Sample Campaign Data

### Campaign: "Shadows of Ravenscroft"

**Basic Information:**
- **Name:** Shadows of Ravenscroft
- **Description:** A gothic horror campaign set in the cursed valley of Ravenscroft, where ancient evils stir and the line between reality and nightmare blurs.
- **World Name:** The Shadowlands
- **Current Date:** 3rd of Harvestmoon, Year of the Crimson Eclipse (1387 DR)

---

## Sample NPCs

### 1. Lady Morgana Blackthorne
```json
{
  "name": "Lady Morgana Blackthorne",
  "race": "Human",
  "gender": "Female",
  "age": 42,
  "occupation": "Noble / Secret Cultist",
  "location_id": 1,
  "personality_traits": ["Charming", "Manipulative", "Obsessed with ancient lore"],
  "ideals": "Knowledge is the ultimate power, regardless of the cost",
  "bonds": "The ancient tome her family has guarded for generations",
  "flaws": "Will sacrifice anyone to achieve her goals",
  "appearance_description": "An elegant woman with prematurely gray hair and piercing green eyes. Always dressed in the finest black silk with silver jewelry.",
  "background": "Born into nobility, Morgana discovered her family's dark secret - they are the hereditary guardians of the Crimson Codex, a tome of forbidden knowledge. She has spent decades studying its contents and slowly implementing its rituals.",
  "stats": {
    "AC": 12,
    "HP": 58,
    "speed": "30 ft.",
    "STR": 10,
    "DEX": 14,
    "CON": 12,
    "INT": 18,
    "WIS": 15,
    "CHA": 16,
    "skills": ["Arcana +7", "Deception +6", "History +7", "Persuasion +6"]
  },
  "relationships": [
    {
      "target_id": 2,
      "target_type": "npc",
      "relationship_type": "employer",
      "description": "Secretly employs Marcus as her agent in town",
      "strength": "strong",
      "public_knowledge": false
    },
    {
      "target_id": 3,
      "target_type": "organization",
      "relationship_type": "leader",
      "description": "Secret leader of the Crimson Circle cult",
      "strength": "strong",
      "public_knowledge": false
    }
  ],
  "status": "active",
  "visibility": "partially_known",
  "voice_description": "Cultured, melodious voice with a slight accent from the old country",
  "notes": "Primary antagonist - players know her as a helpful noble, unaware of her cult activities"
}
```

### 2. Marcus Grimm
```json
{
  "name": "Marcus Grimm",
  "race": "Human",
  "gender": "Male",
  "age": 35,
  "occupation": "Town Blacksmith",
  "location_id": 2,
  "personality_traits": ["Gruff exterior", "Secretly kind-hearted", "Paranoid"],
  "ideals": "Protect the innocent, even if it means getting my hands dirty",
  "bonds": "His late wife's memory drives him to help others",
  "flaws": "Trusts too easily when someone reminds him of his wife",
  "appearance_description": "A burly man with calloused hands and burn scars on his arms. Graying beard and tired eyes that have seen too much.",
  "background": "Once a simple blacksmith who lost his wife to a cult ritual five years ago. Now secretly works to undermine supernatural threats while maintaining his cover as the town smith.",
  "stats": {
    "AC": 14,
    "HP": 45,
    "speed": "30 ft.",
    "STR": 16,
    "DEX": 12,
    "CON": 14,
    "INT": 11,
    "WIS": 13,
    "CHA": 10,
    "skills": ["Athletics +5", "Insight +3", "Investigation +2"]
  },
  "relationships": [
    {
      "target_id": 1,
      "target_type": "npc",
      "relationship_type": "secret_informant",
      "description": "Unknowingly provides information to Lady Morgana while thinking he's helping",
      "strength": "moderate",
      "public_knowledge": false
    },
    {
      "target_id": 4,
      "target_type": "npc",
      "relationship_type": "ally",
      "description": "Works with Father Thomas to protect the town",
      "strength": "strong",
      "public_knowledge": false
    }
  ],
  "status": "active",
  "visibility": "player_known",
  "voice_description": "Deep, gravelly voice with a working-class accent",
  "notes": "Potential ally - tragic backstory could drive character development"
}
```

### 3. Elara Whisperwind
```json
{
  "name": "Elara Whisperwind",
  "race": "Half-Elf",
  "gender": "Female",
  "age": 67,
  "occupation": "Traveling Merchant / Information Broker",
  "location_id": null,
  "personality_traits": ["Mysteriously well-informed", "Speaks in riddles", "Never seems surprised"],
  "ideals": "Information should flow to those who need it most",
  "bonds": "A network of contacts across the realm",
  "flaws": "Sometimes shares information with multiple parties, causing conflicts",
  "appearance_description": "An ageless half-elf with silver-streaked auburn hair and knowing amber eyes. Travels with a wagon full of exotic goods.",
  "background": "A centuries-old information broker who appears when significant events are about to unfold. She trades in secrets as much as goods.",
  "stats": {
    "AC": 15,
    "HP": 52,
    "speed": "30 ft.",
    "STR": 8,
    "DEX": 16,
    "CON": 12,
    "INT": 17,
    "WIS": 18,
    "CHA": 15,
    "skills": ["Insight +7", "Investigation +6", "Perception +7", "Persuasion +5"]
  },
  "relationships": [
    {
      "target_id": 5,
      "target_type": "organization",
      "relationship_type": "informant",
      "description": "Provides information to the Shadowwatch when it serves her purposes",
      "strength": "moderate",
      "public_knowledge": false
    }
  ],
  "status": "active",
  "visibility": "player_known",
  "voice_description": "Soft, melodic voice with careful pronunciation and occasional archaic phrases",
  "notes": "Quest giver and exposition character - use sparingly to avoid deus ex machina"
}
```

---

## Sample Locations

### 1. Blackthorne Manor
```json
{
  "name": "Blackthorne Manor",
  "type": "structure",
  "parent_location_id": 2,
  "population": 12,
  "demographics": {
    "total_population": 12,
    "races": {
      "human": 10,
      "halfling": 2
    },
    "social_classes": {
      "nobility": 1,
      "servants": 11
    }
  },
  "government_type": "Feudal Estate",
  "economic_status": "Wealthy",
  "notable_features": [
    "Gothic architecture with gargoyle decorations",
    "Private library with restricted sections",
    "Hidden ritual chamber in the basement",
    "Well-maintained gardens with exotic plants"
  ],
  "description": "A sprawling gothic manor built on a hill overlooking the town. The architecture is imposing with tall spires, ornate stonework, and stained glass windows depicting ancient family history.",
  "history": "Built 200 years ago by the first Lord Blackthorne, the manor has been the seat of family power for generations. Unknown to most, it was built over an ancient shrine to forgotten gods.",
  "current_events": [
    {
      "event": "Preparation for harvest festival",
      "description": "Lady Morgana is organizing an elaborate harvest festival, but servants whisper about strange preparations"
    }
  ],
  "defenses": "High stone walls, trained guards, magical wards (unknown to most)",
  "trade_goods": [],
  "connected_locations": [
    {
      "location_id": 2,
      "travel_time": "15 minutes",
      "difficulty": "easy",
      "description": "Well-maintained cobblestone road to town"
    }
  ],
  "status": "active",
  "visibility": "player_known",
  "ambient_description": "The air is always slightly cool here, and shadows seem to linger longer than they should. Servants move quietly, and there's often the faint scent of incense.",
  "notes": "Primary antagonist base - players should visit multiple times with increasing access to different areas"
}
```

### 2. Ravenscroft Village
```json
{
  "name": "Ravenscroft Village",
  "type": "settlement",
  "parent_location_id": null,
  "population": 847,
  "demographics": {
    "total_population": 847,
    "races": {
      "human": 780,
      "halfling": 45,
      "dwarf": 15,
      "elf": 7
    },
    "age_distribution": {
      "children": 152,
      "adults": 591,
      "elderly": 104
    },
    "social_classes": {
      "nobility": 1,
      "merchants": 67,
      "craftspeople": 234,
      "laborers": 432,
      "poor": 113
    }
  },
  "government_type": "Village Council with Noble Oversight",
  "economic_status": "Struggling",
  "notable_features": [
    "Ancient stone circle in the town square",
    "Unusually large cemetery for the town size",
    "Fog that never fully clears",
    "Ravens that gather in unusual numbers"
  ],
  "description": "A quaint village nestled in a valley surrounded by dark forests. Cobblestone streets wind between timber-framed buildings, and the town square features an ancient stone circle of unknown origin.",
  "history": "Founded 300 years ago by settlers who claimed the land was 'blessed by the old gods.' The village has survived plagues, famines, and supernatural incidents that drove away neighboring settlements.",
  "current_events": [
    {
      "event": "Missing livestock",
      "description": "Several farms have reported livestock disappearing overnight with no signs of struggle"
    },
    {
      "event": "Harvest festival preparation",
      "description": "The village is preparing for the annual harvest festival, though some elders mutter about bad omens"
    }
  ],
  "defenses": "Village militia (20 members), wooden palisade (partial)",
  "trade_goods": [
    {
      "name": "Wool",
      "type": "textile",
      "quantity": "high",
      "price": 2.5,
      "rarity": "common",
      "seasonal": true,
      "import_export": "export"
    },
    {
      "name": "Preserved Foods",
      "type": "consumable",
      "quantity": "moderate",
      "price": 1.2,
      "rarity": "common",
      "seasonal": false,
      "import_export": "export"
    }
  ],
  "connected_locations": [
    {
      "location_id": 1,
      "travel_time": "15 minutes",
      "difficulty": "easy",
      "description": "Well-maintained road to Blackthorne Manor"
    },
    {
      "location_id": 3,
      "travel_time": "2 hours",
      "difficulty": "moderate",
      "description": "Forest path to the old shrine"
    }
  ],
  "status": "active",
  "visibility": "player_known",
  "ambient_description": "Perpetual mist clings to the streets, and the sound of ravens is ever-present. Locals speak in hushed tones and avoid being out after dark.",
  "notes": "Main hub for player activities - should feel both welcoming and subtly unsettling"
}
```

---

## Sample Organizations

### 1. The Crimson Circle
```json
{
  "name": "The Crimson Circle",
  "type": "religion",
  "scope": "local",
  "headquarters_location_id": null,
  "leader_npc_id": 1,
  "goals": [
    "Awaken the Crimson God from its ancient slumber",
    "Gather sacrificial power through ritual",
    "Eliminate threats to the cult's activities"
  ],
  "methods": [
    "Secret recruitment among the desperate",
    "Ritual sacrifice during significant events",
    "Infiltration of local power structures"
  ],
  "resources": "Funding from Lady Morgana, ancient knowledge, magical artifacts",
  "influence_level": "Hidden but Growing",
  "membership_size": "Small (8 active members)",
  "notable_members": [1, 6, 7],
  "allies": [],
  "enemies": [4, 5],
  "reputation": "Unknown to the general public",
  "status": "active",
  "visibility": "dm_only",
  "notes": "Primary antagonist organization - reveals itself gradually through the campaign"
}
```

### 2. The Shadowwatch
```json
{
  "name": "The Shadowwatch",
  "type": "military",
  "scope": "regional",
  "headquarters_location_id": null,
  "leader_npc_id": null,
  "goals": [
    "Monitor and contain supernatural threats",
    "Protect innocent civilians from otherworldly dangers",
    "Preserve knowledge of supernatural countermeasures"
  ],
  "methods": [
    "Covert surveillance and investigation",
    "Recruitment of capable individuals",
    "Maintenance of hidden safe houses and resources"
  ],
  "resources": "Limited funding, network of informants, specialized equipment",
  "influence_level": "Minor",
  "membership_size": "Small (15 members across the region)",
  "notable_members": [4, 8],
  "allies": [],
  "enemies": [3],
  "reputation": "Rumored to exist among those who deal with supernatural threats",
  "status": "active",
  "visibility": "dm_only",
  "notes": "Potential ally organization - could recruit player characters"
}
```

---

## Sample Plot Hooks

### 1. The Vanishing Livestock
```json
{
  "title": "The Vanishing Livestock",
  "description": "Farm animals around Ravenscroft have been disappearing without a trace. No blood, no signs of struggle, no tracks leading away. The farmers are getting desperate as winter approaches.",
  "hook_type": "mystery",
  "urgency": "moderate",
  "complexity": "moderate",
  "related_npcs": [2, 9],
  "related_locations": [2, 10],
  "related_organizations": [3],
  "prerequisites": [
    {
      "type": "location_visited",
      "target_id": 2,
      "description": "Party must visit Ravenscroft Village"
    }
  ],
  "rewards": {
    "experience": 1200,
    "gold": 200,
    "reputation": "Increased standing with local farmers",
    "information": "First clues about cult activity"
  },
  "consequences": {
    "success": "Cult recruitment slowed, farmers' trust gained, first evidence of supernatural activity",
    "failure": "Cult gains power from sacrifices, farmers lose faith, winter becomes harsher for the village"
  },
  "status": "available",
  "visibility": "player_known",
  "notes": "Entry-level mystery that introduces supernatural elements gradually"
}
```

### 2. The Harvest Festival
```json
{
  "title": "The Harvest Festival",
  "description": "Lady Morgana is organizing an elaborate harvest festival, supposedly to boost morale. However, the timing coincides with a rare celestial alignment, and cult members are making suspicious preparations.",
  "hook_type": "main_quest",
  "urgency": "urgent",
  "complexity": "complex",
  "related_npcs": [1, 2, 4],
  "related_locations": [1, 2],
  "related_organizations": [3, 5],
  "prerequisites": [
    {
      "type": "plot_hook_completed",
      "target_id": 1,
      "description": "Party must have investigated the missing livestock"
    },
    {
      "type": "trust_level",
      "target_id": 2,
      "description": "Marcus Grimm must trust the party enough to share suspicions"
    }
  ],
  "rewards": {
    "experience": 3500,
    "gold": 500,
    "items": ["Silver amulet of protection", "Cult ritual dagger"],
    "story": "Major disruption of cult plans, saving multiple villagers"
  },
  "consequences": {
    "success": "Cult ritual disrupted, Lady Morgana's true nature revealed, village saved from mass sacrifice",
    "failure": "Multiple villagers sacrificed, Crimson God partially awakened, Lady Morgana gains significant power"
  },
  "status": "draft",
  "visibility": "dm_only",
  "notes": "Major climactic event - requires careful timing and multiple session setup"
}
```

---

## Sample Events

### 1. The Great Storm
```json
{
  "title": "The Great Storm",
  "description": "An unseasonable storm struck the valley three nights ago, bringing with it strange red lightning and an eerie silence that followed. Some villagers report seeing shapes moving in the storm clouds.",
  "event_type": "historical",
  "date": "1st of Harvestmoon, Year of the Crimson Eclipse",
  "location_id": 2,
  "participants": [
    {
      "id": 2,
      "type": "location",
      "role": "affected_area"
    }
  ],
  "causes": [
    "Cult ritual partially completed",
    "Weakening of barriers between dimensions",
    "Crimson God's influence growing stronger"
  ],
  "effects": [
    "Livestock began disappearing more frequently",
    "Some villagers report disturbing dreams",
    "Wild animals avoiding the area",
    "Increased supernatural activity"
  ],
  "visibility": "player_known",
  "status": "completed",
  "notes": "Sets the supernatural tone and provides explanation for recent strange events"
}
```

### 2. Market Day Gathering
```json
{
  "title": "Market Day Gathering",
  "description": "The weekly market day in Ravenscroft's town square. Farmers bring goods, traders arrive from neighboring settlements, and information flows as freely as coin.",
  "event_type": "recurring",
  "date": "Every 7th day of the tenday",
  "location_id": 2,
  "participants": [
    {
      "id": 2,
      "type": "npc",
      "role": "regular_trader"
    },
    {
      "id": 3,
      "type": "npc",
      "role": "occasional_visitor"
    }
  ],
  "causes": [
    "Traditional weekly commerce",
    "Social gathering necessity in isolated village"
  ],
  "effects": [
    "Information exchange between villagers and outsiders",
    "Economic activity for local merchants",
    "Opportunity for cult recruitment or player investigation"
  ],
  "visibility": "player_known",
  "status": "active",
  "notes": "Regular event that can serve as a social hub and information gathering opportunity"
}
```

---

## Sample Items

### 1. The Crimson Codex
```json
{
  "name": "The Crimson Codex",
  "type": "artifact",
  "rarity": "artifact",
  "description": "An ancient tome bound in what appears to be deep red leather, though closer inspection reveals disturbing textures. The pages seem to shift and change when not directly observed.",
  "mechanical_effects": {
    "magical_properties": [
      {
        "name": "Forbidden Knowledge",
        "description": "Reading passages grants knowledge of cult rituals and cosmic truths, but risks madness",
        "charges": null,
        "recharge": "none"
      },
      {
        "name": "Whispers of the Crimson God",
        "description": "The book whispers to its reader, slowly corrupting their thoughts and dreams",
        "charges": null,
        "recharge": "continuous"
      }
    ]
  },
  "history": "Written by the first cultists of the Crimson God centuries ago, this tome contains the complete rituals needed to awaken their deity. It has been passed down through the Blackthorne family for generations.",
  "current_owner_id": 1,
  "current_location_id": 1,
  "value": 50000,
  "weight": 5.0,
  "attunement_required": true,
  "status": "active",
  "visibility": "dm_only",
  "notes": "Central MacGuffin - contains both power and corruption. Should be tantalizing but dangerous."
}
```

### 2. Marcus's Silver Hammer
```json
{
  "name": "Marcus's Silver Hammer",
  "type": "weapon",
  "rarity": "uncommon",
  "description": "A well-crafted smithing hammer with silver inlays along the head. The handle is worn smooth from years of use, but the silver gleams as if newly polished.",
  "mechanical_effects": {
    "weapon_properties": {
      "damage": "1d6 + STR",
      "damage_type": "bludgeoning",
      "properties": ["Light", "Thrown (range 20/60)"]
    },
    "magical_properties": [
      {
        "name": "Silver Strike",
        "description": "Deals full damage to creatures vulnerable to silver",
        "charges": null,
        "recharge": "none"
      },
      {
        "name": "Blessing of the Forge",
        "description": "Once per day, can be thrown as a ranged attack with advantage",
        "charges": 1,
        "recharge": "dawn"
      }
    ]
  },
  "history": "Crafted by Marcus himself using silver from his late wife's wedding jewelry. He imbued it with his determination to protect others from the supernatural threats that took her.",
  "current_owner_id": 2,
  "current_location_id": 2,
  "value": 150,
  "weight": 2.5,
  "attunement_required": false,
  "status": "active",
  "visibility": "partially_known",
  "notes": "Potential reward for earning Marcus's trust - represents his personal tragedy and determination"
}
```

---

## Sample AI Chat Scenarios

### Scenario 1: Creating NPCs for a Tavern

**User Message:** "I need some NPCs for the Ravenscroft Inn. The players will probably spend a lot of time there."

**Expected AI Response:**
"Perfect! The Ravenscroft Inn should feel like a cozy refuge in this gothic setting, but with underlying tensions. Given the supernatural atmosphere of your campaign, let me suggest some NPCs that would fit naturally:

**Bartender: Willem Ashford** - A middle-aged man who's run the inn for 15 years. He's seen strange things but learned to keep quiet about them. He could be protective of his guests but nervous about outsiders asking too many questions.

**Regular Patron: Old Henrik** - A retired shepherd who lost his flock in 'the incident' five years ago. He drinks to forget and sometimes mumbles about 'red lights in the sky' and 'things that ain't natural.'

**Serving Girl: Rosie Millbrook** - Young and new to town, she doesn't understand why locals avoid certain topics. Her innocence could make her accidentally helpful to investigators or vulnerable to supernatural threats.

Would you like me to develop any of these further, or should I create full stat blocks for them?"

**Suggested Elements:**
```json
[
  {
    "type": "npc",
    "data": {
      "name": "Willem Ashford",
      "race": "Human",
      "age": 45,
      "occupation": "Innkeeper",
      "personality_traits": ["Protective of guests", "Keeps secrets well", "Nervous around authority"],
      "background": "Has run the inn for 15 years and seen enough strange things to know when to look the other way"
    }
  },
  {
    "type": "npc", 
    "data": {
      "name": "Henrik the Shepherd",
      "race": "Human",
      "age": 68,
      "occupation": "Retired Shepherd",
      "personality_traits": ["Haunted by past events", "Drinks heavily", "Speaks in riddles when drunk"],
      "background": "Lost his entire flock in a supernatural incident five years ago and never recovered"
    }
  }
]
```

### Scenario 2: Developing Plot Consequences

**User Message:** "The players just convinced Marcus to help them investigate Lady Morgana. What would be the realistic consequences of this?"

**Expected AI Response:**
"This is a significant development that would ripple through your campaign in several ways:

**Immediate Consequences:**
- Lady Morgana would notice Marcus's change in behavior if he's been her informant
- Marcus might share his suspicions about the livestock disappearances being connected to cult activity
- Other villagers might become more willing to talk if they see Marcus trusting the party

**Medium-term Effects:**
- Lady Morgana might try to eliminate Marcus as a threat, creating urgency
- The cult might accelerate their timeline, knowing they're being investigated
- Marcus could provide access to locations or information previously unavailable

**Long-term Impact:**
- The village power dynamic shifts - if Marcus is respected, others might follow his lead
- Lady Morgana might need to reveal more of her hand earlier than planned
- The cult might need to find a new source of information about party activities

This could also trigger the 'Harvest Festival' plot hook if Lady Morgana decides she needs to complete her ritual before the investigation progresses further. Would you like me to suggest specific scenes or encounters that could emerge from this development?"

### Scenario 3: Batch Generation Request

**User Message:** "Generate 5 cult members for the Crimson Circle - mix of social classes so they can infiltrate different parts of society."

**Expected AI Response:**
"Excellent idea! A diverse cult membership makes them much more dangerous. Here are five cultists who can operate in different social circles:

1. **Brother Aldric** (Merchant) - Runs the general store, uses his position to identify desperate families for recruitment
2. **Sister Meredith** (Farmer's Wife) - Spreads cult influence among the rural community, knows everyone's secrets  
3. **Brother Tobias** (Village Clerk) - Has access to records and can manipulate official documents
4. **Sister Lyanna** (Seamstress) - Creates cult regalia disguised as normal clothing, popular with village women
5. **Brother Gareth** (Gravedigger) - Handles disposal of evidence, knows about unusual deaths

Each operates under deep cover - they appear to be normal villagers but secretly serve Lady Morgana. Would you like me to develop detailed backgrounds for any of these, or create stat blocks?"

---

## Sample Session Notes

### Session 8: "Secrets in the Shadows"

**Date:** August 15, 2025  
**Session Number:** 8  
**Summary:** The party investigated strange disappearances around Ravenscroft and made contact with Marcus Grimm, uncovering their first hints of supernatural activity.

**Major Events:**
```json
[
  {
    "type": "investigation",
    "description": "Party investigated the Thornfield farm where three sheep vanished",
    "location_id": 10,
    "outcome": "Found strange symbols carved into fence posts, no physical tracks"
  },
  {
    "type": "social_encounter", 
    "description": "Confronted Marcus Grimm about his knowledge of the disappearances",
    "npcs_involved": [2],
    "outcome": "Marcus revealed his suspicions about supernatural causes after party earned his trust"
  },
  {
    "type": "discovery",
    "description": "Marcus shared information about similar incidents five years ago",
    "outcome": "Party learned about 'the incident' that killed Marcus's wife and others"
  }
]
```

**NPC Interactions:**
```json
[
  {
    "npc_id": 2,
    "interaction_type": "conversation",
    "description": "Long discussion about the missing livestock and past supernatural events",
    "relationship_change": "neutral_to_trusted_ally",
    "notes": "Marcus now considers the party allies in protecting the village"
  },
  {
    "npc_id": 9,
    "interaction_type": "brief_encounter",
    "description": "Farmer Thornfield provided details about his missing sheep",
    "relationship_change": "unknown_to_grateful",
    "notes": "Grateful for party's investigation, willing to share more information"
  }
]
```

**Locations Visited:** [2, 10]

**Items Gained/Lost:**
```json
[
  {
    "item_name": "Charcoal rubbing of strange symbols",
    "transaction_type": "gained",
    "description": "Party made rubbings of the symbols found at Thornfield farm"
  }
]
```

**Plot Advancement:**
```json
[
  {
    "plot_hook_id": 1,
    "advancement": "Significant progress - party has identified supernatural cause and gained local ally"
  }
]
```

**Notes:** "Great session for building atmosphere and establishing Marcus as a key ally. Players are starting to suspect something bigger is happening but don't know about the cult yet. Next session should build on Marcus's revelations and maybe introduce more direct supernatural evidence."

---

## AI Session Context Examples

### Example Campaign Context for AI Prompts

```
CAMPAIGN CONTEXT: Shadows of Ravenscroft

WORLD OVERVIEW:
- Gothic horror setting in the cursed Ravenscroft Valley
- Ancient evils stirring, reality and nightmare blurring
- Current date: 3rd of Harvestmoon, Year of the Crimson Eclipse

KEY NPCS:
- Lady Morgana Blackthorne: Noble, secret cult leader, primary antagonist
- Marcus Grimm: Blacksmith, lost wife to cult, now secret ally to party
- Elara Whisperwind: Half-elf merchant, information broker, appears when needed

KEY LOCATIONS:
- Ravenscroft Village: Main hub, population 847, perpetual mist and ravens
- Blackthorne Manor: Lady Morgana's estate, gothic architecture, hidden ritual chamber

ORGANIZATIONS:
- The Crimson Circle: Secret cult led by Lady Morgana, seeks to awaken ancient god
- The Shadowwatch: Regional organization fighting supernatural threats

ACTIVE PLOT HOOKS:
- Missing livestock investigation (in progress)
- Harvest festival preparation (cult planning major ritual)

RECENT EVENTS:
- Great storm three nights ago with red lightning
- Livestock disappearances increasing
- Party gained Marcus Grimm as ally

CAMPAIGN TONE: Gothic horror with mystery elements, supernatural threats hidden beneath normal village life, building tension toward major revelation
```

This comprehensive examples document provides Claude Code with concrete data patterns, realistic content examples, and clear context for how the AI integration should work within the campaign management system.