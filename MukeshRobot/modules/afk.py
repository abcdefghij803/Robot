import asyncio
import time
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from MukeshRobot import pbot, SUPPORT_CHAT
from MukeshRobot.modules.sql.afk_sql import set_afk, rm_afk, is_afk as sql_is_afk
from MukeshRobot.modules.no_sql.afk_db import add_afk, remove_afk, is_afk as nosql_is_afk

# AFK GIF for default replies
AFK_GIF = "https://envs.sh/SAy.mp4"

# Store AFK timestamps
AFK_TIMES = {}

@pbot.on_message(filters.command("afk"))
async def set_afk_status(client, message: Message):
    user_id = message.from_user.id
    reason = "No reason provided"
    
    if len(message.text.split()) > 1:
        reason = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        if message.reply_to_message.photo or message.reply_to_message.sticker:
            reason = "AFK with media!"
    
    # Store AFK timestamp
    AFK_TIMES[user_id] = time.time()

    # Set AFK status in SQL and NoSQL DBs
    set_afk(user_id, reason)  # SQL
    await add_afk(user_id, reason)  # NoSQL
    
    # Reply based on media
    if message.reply_to_message and (message.reply_to_message.photo or message.reply_to_message.sticker):
        if message.reply_to_message.photo:
            await message.reply_photo(
                message.reply_to_message.photo.file_id,
                caption=f"**{message.from_user.first_name} is now AFK!**\n\nReason: `{reason}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_CHAT}")]]
                ),
            )
        elif message.reply_to_message.sticker:
            await message.reply_sticker(
                message.reply_to_message.sticker.file_id,
                caption=f"**{message.from_user.first_name} is now AFK!**\n\nReason: `{reason}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_CHAT}")]]
                ),
            )
    else:
        await message.reply_animation(
            AFK_GIF,
            caption=f"**{message.from_user.first_name} is now AFK!**\n\nReason: `{reason}`",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_CHAT}")]]
            ),
        )

@pbot.on_message(filters.command("back"))
async def remove_afk_status(client, message: Message):
    user_id = message.from_user.id

    # Calculate AFK duration
    afk_time = AFK_TIMES.pop(user_id, None)
    if afk_time:
        duration = time.time() - afk_time
        hours, remainder = divmod(int(duration), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_text = f"{hours}h {minutes}m {seconds}s"
    else:
        time_text = "Unknown duration"

    # Remove AFK status
    rm_afk(user_id)  # SQL
    await remove_afk(user_id)  # NoSQL
    
    await message.reply(f"**{message.from_user.first_name} is no longer AFK!**\nAFK duration: `{time_text}`")

@pbot.on_message(filters.mentioned | filters.reply)
async def afk_reply(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        afk_status, reason = await nosql_is_afk(user_id)  # NoSQL check
        
        if afk_status:
            afk_time = AFK_TIMES.get(user_id, time.time())
            duration = time.time() - afk_time
            hours, remainder = divmod(int(duration), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_text = f"{hours}h {minutes}m {seconds}s"
            
            await message.reply(
                f"**{message.reply_to_message.from_user.first_name}** is currently AFK!\n"
                f"Reason: `{reason}`\nAFK since: `{time_text}`"
            )

@pbot.on_message(filters.group)
async def group_afk_detection(client, message: Message):
    user_id = message.from_user.id
    afk_status, reason = await nosql_is_afk(user_id)

    if afk_status:
        afk_time = AFK_TIMES.pop(user_id, None)
        if afk_time:
            duration = time.time() - afk_time
            hours, remainder = divmod(int(duration), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_text = f"{hours}h {minutes}m {seconds}s"
        else:
            time_text = "Unknown duration"

        rm_afk(user_id)
        await remove_afk(user_id)

        await message.reply(f"**Welcome back, {message.from_user.first_name}!**\nAFK duration: `{time_text}`")

@pbot.on_message(filters.command("afkusers"))
async def list_afk_users(client, message: Message):
    afk_users = await get_afk_users()
    if afk_users:
        users_list = "\n".join([f"User ID: {user['user_id']}, Reason: {user['reason']}" for user in afk_users])
        await message.reply(f"Currently AFK users:\n{users_list}")
    else:
        await message.reply("No users are currently AFK.")

__help__ = """
» Available commands for AFK:

● `/afk` - Set yourself AFK.
● `/afk <reason>` - Set AFK with a reason.
● `/afk <replied to photo or sticker>` - Set AFK with media.
● `/afk <replied to media> <reason>` - Set AFK with media and reason.
● `/back` - Remove AFK status and show AFK duration.

Now bot will automatically remove your AFK when you send a message!
"""

__mod_name__ = "AFK"
