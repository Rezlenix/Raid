"""
Discord Raid Bot - Main Bot Implementation
Handles Discord bot functionality including slash commands and reactions.
"""

import discord
from discord.ext import commands
import logging
import asyncio
from raid_data import RAID_DATA, REACTION_EMOJIS

logger = logging.getLogger(__name__)

class RaidBot(commands.Bot):
    """Discord bot for handling raid commands and reactions."""
    
    def __init__(self):
        # Set up bot intents - enabling message content for traditional commands
        intents = discord.Intents.default()
        intents.message_content = True  # Required for traditional prefix commands
        
        super().__init__(
            command_prefix='!',  # Traditional prefix for !raid command
            intents=intents,
            description="A Discord bot for raid coordination with automatic reactions"
        )
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Setting up bot...")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot has successfully connected to Discord."""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Bot is ready and connected to {len(self.guilds)} guild(s)")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for /raid commands"
        )
        await self.change_presence(activity=activity)
    
    async def on_error(self, event, *args, **kwargs):
        """Handle bot errors."""
        logger.error(f"Bot error in event {event}", exc_info=True)

# Create bot instance
bot = RaidBot()

async def create_raid_embed():
    """
    Create and return the raid embed with participant information.
    """
    embed = discord.Embed(
        title="🗡️ Raid Participants",
        description="Ready for battle!",
        color=discord.Color.red()
    )
    
    # Add raid participants to the embed
    if not RAID_DATA:
        embed.add_field(
            name="No Participants",
            value="No raid participants configured. Please check raid_data.py",
            inline=False
        )
    else:
        # Group participants by their role/text for better organization
        participant_text = ""
        for i, (name, role_text) in enumerate(RAID_DATA.items(), 1):
            participant_text += f"**{i}.** {name} - *{role_text}*\n"
        
        embed.add_field(
            name="Participants",
            value=participant_text,
            inline=False
        )
    
    # Add footer with participant count
    embed.set_footer(text=f"Total participants: {len(RAID_DATA)}")
    
    return embed

@bot.tree.command(name="raid", description="Display raid participants and add reactions")
async def slash_raid_command(interaction: discord.Interaction):
    """
    Slash command to display raid participants with their roles/text.
    Automatically adds reactions to the message.
    """
    try:
        logger.info(f"Slash raid command executed by {interaction.user} in {interaction.guild}")
        
        # Create the raid embed
        embed = await create_raid_embed()
        
        # Respond to the interaction
        await interaction.response.send_message(embed=embed)
        
        # Get the message object to add reactions
        message = await interaction.original_response()
        
        # Add reactions automatically
        await add_reactions_to_message(message)
        
        logger.info(f"Slash raid command completed successfully for {interaction.user}")
        
    except Exception as e:
        logger.error(f"Error in slash raid command: {e}", exc_info=True)
        
        # Send error message to user
        error_embed = discord.Embed(
            title="❌ Error",
            description="An error occurred while processing the raid command.",
            color=discord.Color.red()
        )
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
        except Exception as followup_error:
            logger.error(f"Failed to send error message: {followup_error}")

@bot.command(name="raid")
async def prefix_raid_command(ctx):
    """
    Traditional prefix command (!raid) to display raid participants with their roles/text.
    Automatically adds reactions to the message.
    """
    try:
        logger.info(f"Prefix raid command executed by {ctx.author} in {ctx.guild}")
        
        # Create the raid embed
        embed = await create_raid_embed()
        
        # Send the message
        message = await ctx.send(embed=embed)
        
        # Add reactions automatically
        await add_reactions_to_message(message)
        
        logger.info(f"Prefix raid command completed successfully for {ctx.author}")
        
    except Exception as e:
        logger.error(f"Error in prefix raid command: {e}", exc_info=True)
        
        # Send error message to user
        error_embed = discord.Embed(
            title="❌ Error",
            description="An error occurred while processing the raid command.",
            color=discord.Color.red()
        )
        
        try:
            await ctx.send(embed=error_embed)
        except Exception as followup_error:
            logger.error(f"Failed to send error message: {followup_error}")

async def add_reactions_to_message(message):
    """
    Add reaction emojis to the given message.
    
    Args:
        message: Discord message object to add reactions to
    """
    try:
        logger.info(f"Adding reactions to message {message.id}")
        
        for emoji in REACTION_EMOJIS:
            try:
                await message.add_reaction(emoji)
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            except discord.HTTPException as e:
                logger.warning(f"Failed to add reaction {emoji}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error adding reaction {emoji}: {e}")
        
        logger.info(f"Successfully added {len(REACTION_EMOJIS)} reactions to message")
        
    except Exception as e:
        logger.error(f"Error adding reactions to message: {e}", exc_info=True)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors for traditional commands."""
    logger.error(f"Command error: {error}", exc_info=True)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handle slash command errors."""
    logger.error(f"Slash command error: {error}", exc_info=True)
    
    error_embed = discord.Embed(
        title="❌ Command Error",
        description="An error occurred while executing the command.",
        color=discord.Color.red()
    )
    
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Failed to send error response: {e}")
