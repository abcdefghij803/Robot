import asyncio
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from MukeshRobot import SUPPORT_CHAT, pbot, BOT_USERNAME, OWNER_ID, BOT_NAME

# Track when the bot starts
START_TIME = datetime.now()

PHOTO = [
    "https://envs.sh/STz.jpg",
]

Mukesh = [
    [
        InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇ", url="https://t.me/btw_moon"),
        InlineKeyboardButton(text="ꜱᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"),
    ],
    [
        InlineKeyboardButton(
            text="˹🕸️ ᴛᴧᴘ тᴏ sᴇᴇ ᴍᴧɢɪᴄ 🕸️˼",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
]

# Helper function to calculate uptime
def get_uptime():
    now = datetime.now()
    uptime_sec = (now - START_TIME).total_seconds()
    uptime_str = str(timedelta(seconds=int(uptime_sec)))
    return uptime_str

@pbot.on_message(filters.command("alive"))
async def restart(client, m: Message):
    uptime = get_uptime()
    
    await m.reply_photo(
        PHOTO[0],  # Using the first photo in the PHOTO list
        caption=f"""**Hey {m.from_user.first_name},** \n\n 
I am [{BOT_NAME}](t.me/{BOT_USERNAME}) alive and working since {uptime} ✨🥀 \n\n Made by ➛** [🇲σ᭡፝֟ɳ🌙](https://t.me/btw_moon/557)
        """,
        reply_markup=InlineKeyboardMarkup(Mukesh)
    )
