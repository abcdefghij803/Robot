import html
import json
import re
import requests
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

import MukeshRobot.modules.sql.chatbot_sql as sql
from MukeshRobot import BOT_ID, BOT_NAME, BOT_USERNAME, dispatcher
from MukeshRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from MukeshRobot.modules.log_channel import gloggable

# Google Gemini API Key
GEMINI_API_KEY = "AIzaSyA6s-6vTk5RbSf2FgWFU3hIiuDEim8tub4"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText?key={GEMINI_API_KEY}"

def get_gemini_response(prompt):
    """Fetch response from Google Gemini API."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": {"You are a friendly and playful cat named Meowtastic 🐱. You love to chat with humans in a fun, engaging, and natural way. Keep your responses short, warm, and sometimes a little mischievous—just like a real cat!\nUser: {user_message}\nMeowtastic:": prompt},
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 0.9,
        "max_tokens": 200,
    }
    
    response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        try:
            return result["candidates"][0]["output"]
        except (KeyError, IndexError):
            return "Sorry, I couldn't generate a response."
    else:
        return "Error connecting to AI service."

@user_admin_no_reply
@gloggable
def mukeshrm(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    match = re.match(r"rm_chat(.+?)", query.data)
    if match:
        user_id = match.group(1)
        chat = update.effective_chat
        is_mukesh = sql.set_mukesh(chat.id)
        if is_mukesh:
            sql.set_mukesh(user_id)
            return f"<b>{html.escape(chat.title)}:</b>\nᴄʜᴀᴛʙᴏᴛ ᴅɪꜱᴀʙʟᴇᴅ\n<b>ᴜꜱᴇʀ :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        else:
            update.effective_message.edit_text(
                "{} ᴄʜᴀᴛʙᴏᴛ ᴅɪꜱᴀʙʟᴇᴅ ʙʏ {}.".format(
                    dispatcher.bot.first_name, mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )
    return ""

@user_admin_no_reply
@gloggable
def mukeshadd(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    match = re.match(r"add_chat(.+?)", query.data)
    if match:
        user_id = match.group(1)
        chat = update.effective_chat
        is_mukesh = sql.rem_mukesh(chat.id)
        if is_mukesh:
            sql.rem_mukesh(user_id)
            return f"<b>{html.escape(chat.title)}:</b>\nᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇᴅ\n<b>ᴜꜱᴇʀ :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        else:
            update.effective_message.edit_text(
                "{} ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇᴅ ʙʏ {}.".format(
                    dispatcher.bot.first_name, mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )
    return ""

@user_admin
@gloggable
def mukesh(update: Update, context: CallbackContext):
    message = update.effective_message
    msg = "• ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ"
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data="add_chat({})"),
            InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data="rm_chat({})"),
        ]]
    )
    message.reply_text(
        text=msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )

def mukesh_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "mukesh":
        return True
    elif BOT_USERNAME in message.text.upper():
        return True
    elif reply_message:
        if reply_message.from_user.id == BOT_ID:
            return True
    return False

def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_mukesh = sql.is_mukesh(chat_id)
    
    if is_mukesh:
        return

    if message.text and not message.document:
        if not mukesh_message(context, message):
            return
        
        bot.send_chat_action(chat_id, action="typing")
        response = get_gemini_response(message.text)
        message.reply_text(response)

CHATBOTK_HANDLER = CommandHandler("chatbot", mukesh, run_async=True)
ADD_CHAT_HANDLER = CallbackQueryHandler(mukeshadd, pattern=r"add_chat", run_async=True)
RM_CHAT_HANDLER = CallbackQueryHandler(mukeshrm, pattern=r"rm_chat", run_async=True)
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
    run_async=True,
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTK_HANDLER,
    RM_CHAT_HANDLER,
    CHATBOT_HANDLER,
]
