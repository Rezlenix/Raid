"""
Raid Data Configuration
Contains the raid participants and their associated text/roles.
Also defines the reaction emojis to be added automatically.
"""

# Raid participants with their names and associated text/roles
# Format: "Name": "Role/Description"
RAID_DATA = {
    "Hordis": "Matro a veci na base",
    "Sawag": "Turrety, double doory, veci na turrety",
    "Cloudy": "Bedy, Rakety",
    "Adam": "Boxy, dvere",
    "Zbytek": "Rickyho kity"
}

# Participant-specific reaction emojis based on first letter of names
# Each participant gets a unique letter emoji matching their name
REACTION_EMOJIS = [
    "🇭",  # H for Hordis
    "🇸",  # S for Sawag  
    "🇨",  # C for Cloudy
    "🇦",  # A for Adam
    "🇿"   # Z for Zbytek
]

# Mapping of participants to their letter emojis for easy reference
PARTICIPANT_EMOJIS = {
    "Hordis": "🇭",
    "Sawag": "🇸", 
    "Cloudy": "🇨",
    "Adam": "🇦",
    "Zbytek": "🇿"
}

# Scheduled raids storage (in-memory for now)
# Format: {"raid_id": {"name": "Raid Name", "time": "Schedule", "creator": "User", "participants": []}}
SCHEDULED_RAIDS = {}

# Configuration notes:
# - To modify raid participants, edit the RAID_DATA dictionary above
# - To change reactions, modify the REACTION_EMOJIS list
# - Names should be unique keys in the RAID_DATA dictionary
# - Role text can be any descriptive string
# - Emojis should be standard Unicode emojis for best compatibility
