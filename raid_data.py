"""
Raid Data Configuration
Contains the raid participants and their associated text/roles.
Also defines the reaction emojis to be added automatically.
"""

# Raid participants with their names and associated text/roles
# Format: "Name": "Role/Description"
RAID_DATA = {
    "Alex Thunder": "Tank - Shield Bearer",
    "Sarah Lightbringer": "Healer - Divine Support",
    "Marcus Shadowstrike": "DPS - Stealth Assassin",
    "Elena Firebrand": "DPS - Flame Mage",
    "Thorin Ironforge": "Tank - Heavy Defender",
    "Luna Starweaver": "Support - Buff Specialist",
    "Gareth Swiftstrike": "DPS - Dual Wielder",
    "Aria Frostwind": "DPS - Ice Sorceress",
    "Brock Stormhammer": "DPS - Berserker",
    "Zara Moonwhisper": "Healer - Nature's Guardian"
}

# Reaction emojis to be added automatically to raid messages
# These will be added in order to the raid command message
REACTION_EMOJIS = [
    "⚔️",  # Crossed swords
    "🛡️",  # Shield
    "🏹",  # Bow and arrow
    "✨",  # Sparkles (magic)
    "💪",  # Flexed biceps (strength)
    "🔥",  # Fire
    "❄️",  # Snowflake (ice)
    "⚡",  # Lightning bolt
    "🌟",  # Star
    "👑"   # Crown (leadership)
]

# Configuration notes:
# - To modify raid participants, edit the RAID_DATA dictionary above
# - To change reactions, modify the REACTION_EMOJIS list
# - Names should be unique keys in the RAID_DATA dictionary
# - Role text can be any descriptive string
# - Emojis should be standard Unicode emojis for best compatibility
