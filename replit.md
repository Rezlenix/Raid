# Discord Raid Bot

## Overview

This is a Discord bot designed for raid coordination in gaming communities. The bot provides slash commands for organizing raids and automatically adds reaction emojis to raid messages for easy participation tracking. The application is built using Python and the discord.py library, focusing on simplicity and ease of use for gaming communities.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (July 26, 2025)

- Updated raid participant data to custom Czech/Slovak participants and roles
- Added support for both `/raid` slash command and `!raid` traditional prefix command
- Enabled message content intent for traditional command support
- Created shared embed creation function for both command types
- Implemented comprehensive raid management system with scheduling capabilities
- Added 8 new commands: schedule, join, leave, cancel, raids (both slash and prefix versions)
- Added in-memory raid storage with participant tracking
- Implemented permission checks for raid cancellation (creator or admin only)
- Added reaction-based participation system for scheduled raids

## System Architecture

The application follows a simple, modular architecture with clear separation of concerns:

- **Main Entry Point** (`main.py`): Handles bot initialization, environment configuration, and error handling
- **Bot Implementation** (`bot.py`): Contains the core Discord bot class with event handlers and command setup
- **Data Configuration** (`raid_data.py`): Centralized storage for raid participant data and emoji configurations

The architecture prioritizes maintainability and ease of configuration, allowing non-technical users to modify raid data without touching core bot logic.

## Key Components

### Discord Bot Framework
- **Technology**: discord.py library
- **Architecture**: Event-driven bot using Discord's slash command system
- **Intents**: Configured for message content access and basic guild operations
- **Command System**: Slash commands for modern Discord integration

### Data Management
- **Storage**: Simple Python dictionaries for raid participant data
- **Configuration**: File-based configuration in `raid_data.py`
- **Structure**: Key-value pairs mapping participant names to their roles/descriptions

### Logging System
- **Implementation**: Python's built-in logging module
- **Outputs**: Both console and file logging (`bot.log`)
- **Level**: INFO level for operational monitoring

## Data Flow

1. **Bot Startup**: Main function loads environment variables and initializes bot
2. **Command Registration**: Bot syncs slash commands with Discord API during setup
3. **Command Execution**: Users invoke raid commands through Discord's slash command interface
4. **Response Generation**: Bot processes raid data and generates formatted responses
5. **Reaction Addition**: Bot automatically adds predefined emoji reactions to raid messages

## External Dependencies

### Discord Integration
- **discord.py**: Primary library for Discord API interaction
- **Discord Bot Token**: Required environment variable for authentication
- **Discord Application**: Must be registered through Discord Developer Portal

### Python Runtime
- **Python 3.7+**: Required for discord.py compatibility
- **Standard Library**: Uses asyncio, logging, and os modules
- **No Database**: Currently uses in-memory data storage

## Deployment Strategy

### Environment Configuration
- **Bot Token**: Stored as `DISCORD_BOT_TOKEN` environment variable
- **Security**: Token must be kept secure and not committed to version control

### Runtime Requirements
- **Hosting**: Can run on any Python-capable hosting platform
- **Persistence**: No database required; bot state is ephemeral
- **Scaling**: Single-instance deployment suitable for most Discord servers

### Monitoring
- **Logging**: File-based logging for troubleshooting and monitoring
- **Error Handling**: Graceful error handling with appropriate logging
- **Status**: Bot presence shows current activity status

### Future Considerations
- The simple dictionary-based data storage could be migrated to a database for persistence
- The modular design allows for easy extension with additional commands
- Configuration could be moved to external files (JSON/YAML) for easier management