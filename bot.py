"""
Discord Raid Bot - Main Bot Implementation
Handles Discord bot functionality including slash commands and reactions.
"""

import discord
from discord.ext import commands
import logging
import asyncio
import datetime
import uuid
import aiohttp
import random
from raid_data import RAID_DATA, REACTION_EMOJIS, SCHEDULED_RAIDS, PARTICIPANT_EMOJIS

logger = logging.getLogger(__name__)


async def get_random_dog_gif():
    """Fetch a random dog gif/image from multiple APIs with fallbacks."""
    apis = [
        {
            'url': 'https://random.dog/woof.json',
            'parser': lambda data: data.get('url') if data.get('url') and (data.get('url').endswith('.gif') or data.get('url').endswith('.mp4') or data.get('url').endswith('.webm')) else None
        },
        {
            'url': 'https://dog.ceo/api/breeds/image/random',
            'parser': lambda data: data.get('message') if data.get('status') == 'success' else None
        }
    ]
    
    # Shuffle APIs for randomness
    random.shuffle(apis)
    
    async with aiohttp.ClientSession() as session:
        for api in apis:
            try:
                async with session.get(api['url'], timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = api['parser'](data)
                        if result:
                            # For random.dog, prioritize GIFs and videos
                            if 'random.dog' in api['url']:
                                # Try a few times to get a gif/video from random.dog
                                for attempt in range(3):
                                    if result.endswith(('.gif', '.mp4', '.webm')):
                                        return result
                                    # Try again
                                    async with session.get(api['url'], timeout=aiohttp.ClientTimeout(total=5)) as retry_response:
                                        if retry_response.status == 200:
                                            retry_data = await retry_response.json()
                                            result = api['parser'](retry_data)
                                            if result and result.endswith(('.gif', '.mp4', '.webm')):
                                                return result
                            return result
            except Exception as e:
                logger.warning(f"Failed to fetch from {api['url']}: {e}")
                continue
    
    # Fallback - return a default message if all APIs fail
    return None


class RaidBot(commands.Bot):
    """Discord bot for handling raid commands and reactions."""

    def __init__(self):
        # Set up bot intents - enabling message content for traditional commands
        intents = discord.Intents.default()
        intents.message_content = True  # Required for traditional prefix commands

        super().__init__(
            command_prefix='!',  # Traditional prefix for !raid command
            intents=intents,
            description=
            "A Discord bot for raid coordination with automatic reactions")

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
        if self.user:
            logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(
            f"Bot is ready and connected to {len(self.guilds)} guild(s)")

        # Log registered commands for debugging
        logger.info(
            f"Registered traditional commands: {[cmd.name for cmd in self.commands]}"
        )
        logger.info(f"Command prefix: {self.command_prefix}")

        # Set bot status
        activity = discord.Activity(type=discord.ActivityType.watching,
                                    name="for /raid and !raid commands")
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
    embed = discord.Embed(title="🗡️ Raid Participants",
                          description="Ready for battle!",
                          color=discord.Color.red())

    # Add raid participants to the embed
    if not RAID_DATA:
        embed.add_field(
            name="No Participants",
            value="No raid participants configured. Please check raid_data.py",
            inline=False)
    else:
        # Group participants by their role/text with custom emojis
        participant_text = ""
        for i, (name, role_text) in enumerate(RAID_DATA.items(), 1):
            emoji = PARTICIPANT_EMOJIS.get(
                name, "⚔️")  # Default to sword if not found
            participant_text += f"{emoji} **{name}** - *{role_text}*\n"

        embed.add_field(name="Participants",
                        value=participant_text,
                        inline=False)

    # Add footer with participant count
    embed.set_footer(text=f"Total participants: {len(RAID_DATA)}")

    return embed


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

        logger.info(
            f"Successfully added {len(REACTION_EMOJIS)} reactions to message")

    except Exception as e:
        logger.error(f"Error adding reactions to message: {e}", exc_info=True)


# === SLASH COMMANDS ===


@bot.tree.command(name="raid",
                  description="Display raid participants and add reactions")
async def slash_raid_command(interaction: discord.Interaction):
    """
    Slash command to display raid participants with their roles/text.
    Automatically adds reactions to the message.
    """
    try:
        logger.info(
            f"Slash raid command executed by {interaction.user} in {interaction.guild}"
        )

        # Create the raid embed
        embed = await create_raid_embed()

        # Respond to the interaction
        await interaction.response.send_message(embed=embed)

        # Get the message object to add reactions
        message = await interaction.original_response()

        # Add reactions automatically
        await add_reactions_to_message(message)

        logger.info(
            f"Slash raid command completed successfully for {interaction.user}"
        )

    except Exception as e:
        logger.error(f"Error in slash raid command: {e}", exc_info=True)

        # Send error message to user
        error_embed = discord.Embed(
            title="❌ Error",
            description="An error occurred while processing the raid command.",
            color=discord.Color.red())

        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=error_embed,
                                                ephemeral=True)
            else:
                await interaction.response.send_message(embed=error_embed,
                                                        ephemeral=True)
        except Exception as followup_error:
            logger.error(f"Failed to send error message: {followup_error}")


@bot.tree.command(name="wipe",
                  description="Display wipe schedule for Rust servers")
async def slash_wipe_command(interaction: discord.Interaction):
    """Slash command to display wipe schedule."""
    try:
        logger.info(f"Slash wipe command executed by {interaction.user.name}")

        embed = discord.Embed(
            title="🗓️ Wipe Schedule",
            description=
            "US 2x Quad - Pondělí a pátek 20:00 - connect us2xq.warbandits.gg\nUS 2x Max5 - Úterý a sobota 20:00 - connect us2xm5.warbandits.gg\nUS 2x Trio - Neděle a čtvrtek 20:00 - connect us2xt.warbandits.gg",
            color=discord.Color.blue())

        await interaction.response.send_message(embed=embed)
        logger.info(
            f"Slash wipe command completed successfully for {interaction.user.name}"
        )

    except Exception as e:
        logger.error(f"Error in slash wipe command: {e}", exc_info=True)
        await interaction.response.send_message(
            "❌ Error displaying wipe schedule.", ephemeral=True)


@bot.tree.command(name="cotr", description="Display COTR guide link")
async def slash_cotr_command(interaction: discord.Interaction):
    """Slash command to display COTR guide link."""
    try:
        logger.info(f"Slash cotr command executed by {interaction.user.name}")

        embed = discord.Embed(
            title="📖 COTR Guide",
            description=
            "https://docs.google.com/document/d/1BXhyJs94A_Hh1RGt3ptsjJbKjzDsRGABtCC9HSM-m7c/edit?usp=sharing",
            color=discord.Color.green())

        await interaction.response.send_message(embed=embed)
        logger.info(
            f"Slash cotr command completed successfully for {interaction.user.name}"
        )

    except Exception as e:
        logger.error(f"Error in slash cotr command: {e}", exc_info=True)
        await interaction.response.send_message(
            "❌ Error displaying COTR guide.", ephemeral=True)


@bot.tree.command(name="susa", description="Send a random dog meme gif")
async def slash_susa_command(interaction: discord.Interaction):
    """Slash command to send a random dog meme gif."""
    try:
        logger.info(f"Slash susa command executed by {interaction.user.name}")
        
        # Defer the response since fetching might take a moment
        await interaction.response.defer()
        
        # Get random dog gif
        dog_url = await get_random_dog_gif()
        
        if dog_url:
            embed = discord.Embed(
                title="🐕 Random Dog Meme",
                color=discord.Color.orange()
            )
            embed.set_image(url=dog_url)
            await interaction.followup.send(embed=embed)
            logger.info(f"Slash susa command completed successfully for {interaction.user.name}")
        else:
            await interaction.followup.send("❌ Sorry, couldn't fetch a dog gif right now. Try again!")
            logger.warning(f"Slash susa command failed to fetch gif for {interaction.user.name}")
        
    except Exception as e:
        logger.error(f"Error in slash susa command: {e}", exc_info=True)
        await interaction.followup.send("❌ Error fetching dog meme.", ephemeral=True)


# === TRADITIONAL PREFIX COMMANDS ===


@bot.command(name="raid")
async def prefix_raid_command(ctx):
    """
    Traditional prefix command (!raid) to display raid participants with their roles/text.
    Automatically adds reactions to the message.
    """
    try:
        logger.info(
            f"Prefix raid command executed by {ctx.author} in {ctx.guild}")

        # Create the raid embed
        embed = await create_raid_embed()

        # Send the message
        message = await ctx.send(embed=embed)

        # Add reactions automatically
        await add_reactions_to_message(message)

        logger.info(
            f"Prefix raid command completed successfully for {ctx.author}")

    except Exception as e:
        logger.error(f"Error in prefix raid command: {e}", exc_info=True)

        # Send error message to user
        error_embed = discord.Embed(
            title="❌ Error",
            description="An error occurred while processing the raid command.",
            color=discord.Color.red())

        try:
            await ctx.send(embed=error_embed)
        except Exception as followup_error:
            logger.error(f"Failed to send error message: {followup_error}")


@bot.command(name="schedule")
async def prefix_schedule_command(ctx,
                                  raid_name: str,
                                  time: str,
                                  *,
                                  description: str = ""):
    """
    Traditional prefix command to schedule a new raid.
    Usage: !schedule "Raid Name" "Time" Description
    """
    try:
        logger.info(f"Prefix schedule command executed by {ctx.author}")

        # Generate unique raid ID
        raid_id = str(uuid.uuid4())[:8]

        # Store raid information
        SCHEDULED_RAIDS[raid_id] = {
            "name": raid_name,
            "time": time,
            "description": description,
            "creator": str(ctx.author),
            "participants": [],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # Create embed
        embed = discord.Embed(title="📅 Raid Scheduled",
                              color=discord.Color.green())
        embed.add_field(name="Raid Name", value=raid_name, inline=True)
        embed.add_field(name="Time", value=time, inline=True)
        embed.add_field(name="Raid ID", value=raid_id, inline=True)
        if description:
            embed.add_field(name="Description",
                            value=description,
                            inline=False)
        embed.add_field(name="Created by",
                        value=ctx.author.mention,
                        inline=True)
        embed.add_field(name="Participants", value="None yet", inline=True)
        embed.set_footer(text=f"Use !join {raid_id} to participate")

        message = await ctx.send(embed=embed)

        # Add reactions for join/leave
        await message.add_reaction("✅")  # Join
        await message.add_reaction("❌")  # Leave

        logger.info(f"Raid scheduled successfully: {raid_id}")

    except Exception as e:
        logger.error(f"Error in prefix schedule command: {e}", exc_info=True)
        await ctx.send("❌ Error scheduling raid.")


@bot.command(name="join")
async def prefix_join_command(ctx, raid_id: str):
    """
    Traditional prefix command to join a scheduled raid.
    """
    try:
        if raid_id not in SCHEDULED_RAIDS:
            await ctx.send("❌ Raid not found.")
            return

        raid = SCHEDULED_RAIDS[raid_id]
        user_name = str(ctx.author)

        if user_name in raid["participants"]:
            await ctx.send("⚠️ You're already participating in this raid.")
            return

        raid["participants"].append(user_name)

        embed = discord.Embed(
            title="✅ Joined Raid",
            description=f"You've joined the raid: **{raid['name']}**",
            color=discord.Color.green())
        embed.add_field(name="Time", value=raid["time"], inline=True)
        embed.add_field(name="Participants",
                        value=f"{len(raid['participants'])}",
                        inline=True)

        await ctx.send(embed=embed)
        logger.info(f"{user_name} joined raid {raid_id}")

    except Exception as e:
        logger.error(f"Error in prefix join command: {e}", exc_info=True)
        await ctx.send("❌ Error joining raid.")


@bot.command(name="leave")
async def prefix_leave_command(ctx, raid_id: str):
    """
    Traditional prefix command to leave a scheduled raid.
    """
    try:
        if raid_id not in SCHEDULED_RAIDS:
            await ctx.send("❌ Raid not found.")
            return

        raid = SCHEDULED_RAIDS[raid_id]
        user_name = str(ctx.author)

        if user_name not in raid["participants"]:
            await ctx.send("⚠️ You're not participating in this raid.")
            return

        raid["participants"].remove(user_name)

        embed = discord.Embed(
            title="❌ Left Raid",
            description=f"You've left the raid: **{raid['name']}**",
            color=discord.Color.orange())

        await ctx.send(embed=embed)
        logger.info(f"{user_name} left raid {raid_id}")

    except Exception as e:
        logger.error(f"Error in prefix leave command: {e}", exc_info=True)
        await ctx.send("❌ Error leaving raid.")


@bot.command(name="cancel")
async def prefix_cancel_command(ctx, raid_id: str):
    """
    Traditional prefix command to cancel a scheduled raid.
    """
    try:
        if raid_id not in SCHEDULED_RAIDS:
            await ctx.send("❌ Raid not found.")
            return

        raid = SCHEDULED_RAIDS[raid_id]

        # Check if user is the creator or has admin permissions
        if str(ctx.author) != raid[
                "creator"] and not ctx.author.guild_permissions.administrator:
            await ctx.send(
                "❌ Only the raid creator or administrators can cancel raids.")
            return

        raid_name = raid["name"]
        participants_count = len(raid["participants"])

        # Remove the raid
        del SCHEDULED_RAIDS[raid_id]

        embed = discord.Embed(
            title="🚫 Raid Cancelled",
            description=f"The raid **{raid_name}** has been cancelled.",
            color=discord.Color.red())
        embed.add_field(name="Participants Notified",
                        value=f"{participants_count}",
                        inline=True)
        embed.add_field(name="Cancelled by",
                        value=ctx.author.mention,
                        inline=True)

        await ctx.send(embed=embed)
        logger.info(f"Raid {raid_id} cancelled by {ctx.author}")

    except Exception as e:
        logger.error(f"Error in prefix cancel command: {e}", exc_info=True)
        await ctx.send("❌ Error cancelling raid.")


@bot.command(name="raids")
async def prefix_raids_command(ctx):
    """
    Traditional prefix command to list all scheduled raids.
    """
    try:
        if not SCHEDULED_RAIDS:
            embed = discord.Embed(title="📅 Scheduled Raids",
                                  description="No raids currently scheduled.",
                                  color=discord.Color.blue())
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="📅 Scheduled Raids",
                              color=discord.Color.blue())

        for raid_id, raid in SCHEDULED_RAIDS.items():
            participants_text = f"{len(raid['participants'])} participants"
            if raid['participants']:
                participants_text += f": {', '.join(raid['participants'][:3])}"
                if len(raid['participants']) > 3:
                    participants_text += f" (+{len(raid['participants']) - 3} more)"

            embed.add_field(
                name=f"🗡️ {raid['name']} (ID: {raid_id})",
                value=
                f"**Time:** {raid['time']}\n**Creator:** {raid['creator']}\n**Participants:** {participants_text}",
                inline=False)

        embed.set_footer(text="Use !join <raid_id> to participate")
        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in prefix raids command: {e}", exc_info=True)
        await ctx.send("❌ Error listing raids.")


@bot.command(name="wipe")
async def prefix_wipe_command(ctx):
    """Traditional prefix command to display wipe schedule."""
    try:
        logger.info(f"Prefix wipe command executed by {ctx.author}")

        embed = discord.Embed(
            title="🗓️ Wipe Schedule",
            description=
            "US 2x Quad - Pondělí a pátek 20:00 - connect us2xq.warbandits.gg\nUS 2x Max5 - Úterý a sobota 20:00 - connect us2xm5.warbandits.gg\nUS 2x Trio - Neděle a čtvrtek 20:00 - connect us2xt.warbandits.gg",
            color=discord.Color.blue())

        await ctx.send(embed=embed)
        logger.info(
            f"Prefix wipe command completed successfully for {ctx.author}")

    except Exception as e:
        logger.error(f"Error in prefix wipe command: {e}", exc_info=True)
        await ctx.send("❌ Error displaying wipe schedule.")


@bot.command(name="cotr")
async def prefix_cotr_command(ctx):
    """Traditional prefix command to display COTR guide link."""
    try:
        logger.info(f"Prefix cotr command executed by {ctx.author}")

        embed = discord.Embed(
            title="📖 Clash of the Rust Guidelines",
            description=
            "https://docs.google.com/document/d/1BXhyJs94A_Hh1RGt3ptsjJbKjzDsRGABtCC9HSM-m7c/edit?usp=sharing",
            color=discord.Color.green())

        await ctx.send(embed=embed)
        logger.info(
            f"Prefix cotr command completed successfully for {ctx.author}")

    except Exception as e:
        logger.error(f"Error in prefix cotr command: {e}", exc_info=True)
        await ctx.send("❌ Error displaying COTR guide.")


@bot.command(name="susa")
async def prefix_susa_command(ctx):
    """Traditional prefix command to send a random dog meme gif."""
    try:
        logger.info(f"Prefix susa command executed by {ctx.author}")
        
        # Send thinking message
        thinking_msg = await ctx.send("🐕 Fetching a random dog meme...")
        
        # Get random dog gif
        dog_url = await get_random_dog_gif()
        
        if dog_url:
            embed = discord.Embed(
                title="🐕 Random Dog Meme",
                color=discord.Color.orange()
            )
            embed.set_image(url=dog_url)
            await thinking_msg.edit(content="", embed=embed)
            logger.info(f"Prefix susa command completed successfully for {ctx.author}")
        else:
            await thinking_msg.edit(content="❌ Sorry, couldn't fetch a dog gif right now. Try again!")
            logger.warning(f"Prefix susa command failed to fetch gif for {ctx.author}")
        
    except Exception as e:
        logger.error(f"Error in prefix susa command: {e}", exc_info=True)
        await ctx.send("❌ Error fetching dog meme.")


# === ERROR HANDLERS ===


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors for traditional commands."""
    logger.error(f"Command error: {error}", exc_info=True)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction,
                               error: discord.app_commands.AppCommandError):
    """Handle slash command errors."""
    logger.error(f"Slash command error: {error}", exc_info=True)

    error_embed = discord.Embed(
        title="❌ Command Error",
        description="An error occurred while executing the command.",
        color=discord.Color.red())

    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=error_embed,
                                                    ephemeral=True)
    except Exception as e:
        logger.error(f"Failed to send error response: {e}")
