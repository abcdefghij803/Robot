import html
import requests
import re
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
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
from MukeshRobot import BOT_ID, BOT_USERNAME, dispatcher
from MukeshRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from MukeshRobot.modules.log_channel import gloggable

# ✅ Correct Gemini API Key (Make sure this is valid)
GEMINI_API_KEY = "AIzaSyBrMUGQvi3QcpjlIElaieCplhJquHhdGCg"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateText?key={GEMINI_API_KEY}"

def get_gemini_response(user_message):
    """Google Gemini API se response fetch kare"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"You are a friendly and playful cat named Meowtastic 🐱. You love to chat with humans in a fun, engaging, and natural way. Keep your responses short, warm, and sometimes a little mischievous—just like a real cat!\nUser: {user_message}\nMeowtastic:"}]}]
    }
    
    response = requests.post(GEMINI_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            result = response.json()
            return result["candidates"][0]["output"]  # ✅ Corrected Key
        except (KeyError, IndexError):
            return "Meow... I couldn't understand that. Try again! 🐱"
    else:
        return "Error connecting to AI service. Please try again later."

def chatbot(update: Update, context: CallbackContext):
    """Telegram chatbot handler"""
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_mukesh = sql.is_mukesh(chat_id)

    if is_mukesh:
        return

    if message.text and not message.document:
        bot.send_chat_action(chat_id, action="typing")
        response = get_gemini_response(message.text)
        message.reply_text(response)

# ✅ Handlers
CHATBOT_HANDLER = MessageHandler(Filters.text & ~Filters.command, chatbot, run_async=True)

# ✅ Adding Handlers to Dispatcher
dispatcher.add_handler(CHATBOT_HANDLER)
