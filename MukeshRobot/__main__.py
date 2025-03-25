import importlib
import re
import time
import asyncio
from platform import python_version as y
from sys import argv
from pyrogram import __version__ as pyrover
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlhver

import MukeshRobot.modules.no_sql.users_db as sql
from MukeshRobot import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)
from MukeshRobot.modules import ALL_MODULES
from MukeshRobot.modules.helper_funcs.chat_status import is_user_admin
from MukeshRobot.modules.helper_funcs.misc import paginate_modules


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

PM_START_TEXT = """ 
*Hi* {} 
Nice to meet you !

I am Meowsteric bot 😺 
A powerful stable and cute telegram music and management bot.
"""

buttons = [
    [
        InlineKeyboardButton(
            text="+ Add me to your clan darlo +",
            url=f"https://t.me/{dispatcher.bot.username}?startgroup=true",
        ),
    ],
   [
        InlineKeyboardButton(text="⭐ About me⭐", callback_data="mukesh_"),
        InlineKeyboardButton(text="✨ Help ✨", callback_data="Main_help"),
      ],    
   [
        InlineKeyboardButton(text="❄ Owner ❄", callback_data="advance_help"),
        InlineKeyboardButton(text="🎄 Update 🎄", url=f"t.me/kittyxupdates"),
      ],    

]

HELP_STRINGS = f"""
» *{BOT_NAME}  present it's feature choose a module to get help about it ✨*"""

DONATE_STRING = f"""Hey, i am glad to know you are interested in donating us that mean a lot :)

We provide 24×7 managment and music service so we also need some help for it, donate now via:-
• Upi id » Kittyxupdates 
• You can also donate by contacting [developer](https://t.me/about_ur_moonshining/5) ✅

Your small amount can help us and Meowsteric to grow more ✨"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("MukeshRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMG,
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )

def start(update: Update, context: CallbackContext):
    args = context.args
    global uptime
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="◀", callback_data="help_back")]]
                    ),
                )
            elif args[0].lower() == "markdownhelp":
                IMPORTED["exᴛʀᴀs"].markdown_help_sender(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rᴜʟᴇs" in IMPORTED:
                IMPORTED["rᴜʟᴇs"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            
            x=update.effective_message.reply_sticker(
                "CAACAgUAAxkBAAEBmL1nBos4F1-tUjWNnjl5r5cne-xpCQACHgoAAsmuGVVnKBvEVZZMvB4E")
            
            update.effective_message.reply_photo(START_IMG,PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME,sql.num_users(),sql.num_chats()),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_photo(
            START_IMG,
            caption="ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ  !\n<b>ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ​:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "» *Available commans for​​* *{}* :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_caption(text,
                parse_mode=ParseMode.MARKDOWN,
                
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back", callback_data="help_back"),InlineKeyboardButton(text="Support", callback_data="mukesh_support")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_caption(HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def Mukesh_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "mukesh_":
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_caption(f"*Hi i am {dispatcher.bot.first_name}*"
            "\n*A powerful and awesome telegram group management and music player that gives you spam-free and fun environment for your groups :)*"
            "\n\n/*● I can restrict users.*"
            "\n● I can greet users with customizable welcome messages and even set a group's rules."
            "\n● I have a music player system."
            "\n● I have almost all awaited group managing features like ban, mute, welcome, kick, federation, and many more."
            "\n● I have a note-keeping system, blacklists, and even predetermined replies on certain keywords."
            "\n● I check for admins' permissions before executing any command and more stuff"
            f"\n\n➻ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ғᴏʀ ɢᴇᴛᴛɪɴɢ ʙᴀsɪᴄ ʜᴇʟᴩ ᴀɴᴅ ɪɴғᴏ ᴀʙᴏᴜᴛ {dispatcher.bot.first_name}.",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="• Meowsteric v2.0 •", callback_data="expert_help"),
                    ],
                    [
                        InlineKeyboardButton(
                            text="⭐ Support ⭐", callback_data="mukesh_support"
                        ),
                        InlineKeyboardButton(
                            text="Guide 📃", callback_data="basic_help"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="👨‍💻Developer", callback_data="advance_help"
                        ),
                        InlineKeyboardButton(
                            text="🥀Source",
                            callback_data="source_",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="• Home •", callback_data="mukesh_back"),
                    ],
                ]
            ),
        )
    elif query.data == "mukesh_support":
        query.message.edit_caption("**๏ Click on the button to get more about me**"
            f"\n\nIf you find any error or bug on bot or want to give any feedback about the bot then you are welcome to support chat  (✿◠‿◠).",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="⭐ Support ⭐", url=f"https://t.me/+vhymK8YMHA5iNTU9"
                        ),
                        InlineKeyboardButton(
                            text="🥀 Update 🥀", url=f"t.me/kittyxupdates"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="👩‍💻 Developer 👩‍💻", callback_data="advance_help"
                        ),
                        InlineKeyboardButton(
                            text="💡 Study 💡", url="https://t.me/PWM_discussion"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="• Back •", callback_data="mukesh_"),
                    ],
                ]
            ),
        )
    elif query.data == "mukesh_back":
        first_name = update.effective_user.first_name 
        query.message.edit_caption(PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME,sql.num_users(),sql.num_chats()),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
        )
def MukeshRobot_Main_Callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "Main_help":
        query.message.edit_caption(f"""
 {BOT_NAME} help menu ✨
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🎄 Galaxy 🎄", callback_data="moon_")
                    ],                
                    [
                        InlineKeyboardButton(text="Music 🎧", callback_data="Music_"),
                        InlineKeyboardButton(text="Managment ✔", callback_data="help_back")
                    ],                    
                    [
                        InlineKeyboardButton(text="Basic guide 📃", callback_data="basic_help"),
                        InlineKeyboardButton(text="Donate ❄", callback_data="donation_help") 
                    ],
                    [InlineKeyboardButton(text="• Home •", callback_data="mukesh_back")]
                ]
            ),
        )
    elif query.data=="basic_help":
        query.message.edit_caption("""Hey This is a small and quick guide to meowsteric bot 🎉

1. Click on the "Add me to your clan" button
2. Select your group name.
3. Give the bot all the privileges to work smoothly and at full capacity. 

For get command you can choose your preference music or management. 
If you still face any problems you are always welcome to support ✨""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="Music 🎧", callback_data="Music_"),
                        InlineKeyboardButton(text="Managment ⭐", callback_data="help_back") 
                    ],
                    [InlineKeyboardButton(text="• Back •", callback_data="Main_help")]
                ]
            ),
        )
    elif query.data=="mukesh_back":
        query.message.edit_caption("""Exᴘᴇʀᴛ ᴄᴏᴍᴍᴀɴᴅs

👥 Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs
👮🏻 Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Aᴅᴍɪɴs & Mᴏᴅᴇʀᴀᴛᴏʀs.
🕵🏻 Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Aᴅᴍɪɴs

🕵🏻  /unbanall ᴍᴇᴍʙᴇʀs ғʀᴏᴍ ʏᴏᴜʀ ɢʀᴏᴜᴘs
👮🏻  /unmuteall ᴜɴᴍᴜᴛᴇᴀʟʟ ᴀʟʟ ғʀᴏᴍ Yᴏᴜʀ Gʀᴏᴜᴘ

Pɪɴɴᴇᴅ Mᴇssᴀɢᴇs
🕵🏻  /pin [ᴍᴇssᴀɢᴇ] sᴇɴᴅs ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛʜʀᴏᴜɢʜ ᴛʜᴇ Bᴏᴛ ᴀɴᴅ ᴘɪɴs ɪᴛ.
🕵🏻  /pin ᴘɪɴs ᴛʜᴇ ᴍᴇssᴀɢᴇ ɪɴ ʀᴇᴘʟʏ
🕵🏻  /unpin ʀᴇᴍᴏᴠᴇs ᴛʜᴇ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ.
🕵🏻  /adminlist ʟɪsᴛ ᴏғ ᴀʟʟ ᴛʜᴇ sᴘᴇᴄɪᴀʟ ʀᴏʟᴇs ᴀssɪɢɴᴇᴅ ᴛᴏ ᴜsᴇʀs.

◽️ /bug: (ᴍᴇssᴀɢᴇ) ᴛᴏ Sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴇʀʀᴏʀs ᴡʜɪᴄʜ ʏᴏᴜ ᴀʀᴇ ғᴀᴄɪɴɢ 
ᴇx: /bug Hᴇʏ Tʜᴇʀᴇ Is ᴀ Sᴏᴍᴇᴛʜɪɴɢ Eʀʀᴏʀ @username ᴏғ ᴄʜᴀᴛ! .""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
               [
                    [
                        InlineKeyboardButton(text="Developer 👩‍💻", callback_data="advance_help"),
                        InlineKeyboardButton(text="• Support •", callback_data="mukesh_support") 
                    ],
                    [InlineKeyboardButton(text="• Back •", callback_data="Main_help")]
                ]
            ),
        )             
    elif query.data=="advance_help":
        query.message.edit_caption("""Hey,

I am Meowsteric bot ✨
I am created with love by my [🇲σ᭡፝֟ɳ🌙](https://t.me/About_ur_Moonshining/5) ❤.""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
               [
                    [
                        InlineKeyboardButton(text="🇲σ᭡፝֟ɳ🌙", url=f"https://t.me/About_ur_Moonshining/5"),
                        InlineKeyboardButton(text="Owner's clan 🎄", url=f"https://t.me/+vhymK8YMHA5iNTU9") 
                    ],                    
                    [
                        InlineKeyboardButton(text="🎄 Galaxy 🎄", callback_data="moon_"),
                        InlineKeyboardButton(text="⭐ Help ⭐", callback_data="Main_help")
                    ],
                    [InlineKeyboardButton(text="• Home •", callback_data="mukesh_back"),]
               ]
            ),
        )
    elif query.data=="expert_help":
        query.message.edit_caption(f"""We have added or upgraded the following plugins given below ✨

• Added ai response and ai img(chat-gpt).
• Added quotly.
• Added cricket score.
• Added emoji game.
• Update howsall, judge, wish, afk feature.
• Update write, bug and fedration tools.
• Added gif and animated sticker kang also.
• Added Website of bot for preview.
• Added Pinterest,yt and Insta video downloader.
• Added Ph logo as img and sticker.
• Added inbuilt music system.

For more info about Meowsteric updates check website 🎄👀""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
               [
                    [
                        InlineKeyboardButton(text="⭐ Support ⭐", url=f"https://t.me/+vhymK8YMHA5iNTU9"),
                        InlineKeyboardButton(text="🥀 Updates 🥀", url=f"t.me/kittyxupdates")
                    ],                    
                    [
                        InlineKeyboardButton(text="👩‍💻 Developer 👩‍💻", callback_data="advance_help"),
                        InlineKeyboardButton(text="💡 Github 💡", url="https://t.me/pwmbothub") 
                    ],
                    [InlineKeyboardButton(text="• Back •", callback_data="mukesh_"),]
               ]
            ),
        )
    elif query.data=="donation_help":
        query.message.edit_caption("""Hey, i am glad to know you are interested in donating us that mean a lot :)

We provide 24×7 managment and music service so we also need some help for it, donate now via:-
• Upi id » @kittyxupdates
• You can also donate by contacting [developer](https://t.me/about_ur_moonshining/5) ✅

Your small amount can help us and meowsteric to grow more ✨""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [ 
                    [
                        InlineKeyboardButton(text="• Donate •", url="https://t.me/kittyxupdates"),InlineKeyboardButton(text="• Support •", callback_data="mukesh_support")
                    ]
                ]
            ),
            )  
def Moon_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "moon_":
        query.message.edit_caption(
            f"""
Join our groups....🧊

For more info about meowsteric updates check support 🎄👀
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Study 🥂", url=f"https://t.me/PWM_discussion"
                        ),
                        InlineKeyboardButton(
                            text="Meowsteric updates🥀", url=f"t.me/kittyxupdates"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Developer 👨‍💻", callback_data="advance_help"
                        ),
                        InlineKeyboardButton(
                            text="Share ur query💡", url="https://t.me/pwmbothub"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="• Back •", callback_data="Main_help"),
                    ],
                ]
            ),
        )  
    elif query.data == "moon_back":
        first_name = update.effective_user.first_name
        query.message.edit_caption(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME,sql.num_users(),sql.num_chats()),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            
        )

def Source_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "source_":
        gif_url = "https://files.catbox.moe/6bslyh.mp4"
        user_mention = f"[{query.from_user.first_name}](tg://user?id={query.from_user.id})"
        
        query.message.reply_animation(
            animation=gif_url,
            caption=f"Close by {user_mention}",
            parse_mode="Markdown",
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_caption(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME,sql.num_users(),sql.num_chats()),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            
        )

        
def Music_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "Music_":
        query.message.edit_caption(f"""
 Hi, i am a Meowsteric X player ...

Here is the help menu for Meowsteric music player ✨👀
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [                    
                    [
                        InlineKeyboardButton(
                            text="• Admin •", callback_data="Music_admin"
                        ),
                        InlineKeyboardButton(
                            text="• User •", callback_data="Music_play"
                        ),
                        InlineKeyboardButton(text="• Sudo •", callback_data="Music_bot"
                        ),
                        ],
                    [
                        InlineKeyboardButton(text="✨ Extra ✨", callback_data="Music_extra"),InlineKeyboardButton(text="• Back •", callback_data="Main_help")
                    ]
                ]
            ),
            )  
    elif query.data == "Music_admin":
        query.message.edit_caption(f"*✨ Admin commands :*"
            f"""
● /playforce <query> or <replied to audio>:stop ongoing stream and play your searched music.
● /vplayforce <query> or <replied to audio>:stop ongoing stream and play your searched video.
● /skip: skip your current track from vc.
● /pause: pause your outgoing stream on group.
● /resume: resume your paused stream.
● /end: end your videochat.
● /seek <seconds in number>: number of second you want to seek in current track
● /seekback <seconds in number>: number of second you want to seek back in current track
● /end: end your videochat.
● /auth: add user to authorized list that can use admin's command without be a admin.
● /unauth: remove user from authorized list.
● /authusers: list all auths of chat 

☆✧....𝐁𝐘🫧 » [☄️𝐌ᴏᴏɴ🌙](https://t.me/About_ur_Moonshining/5)....🥀🥀✧☆

(✿◠‿◠)
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=" • Back • ", callback_data="Music_"),InlineKeyboardButton(text="Support", callback_data="mukesh_support")
                    ]
                ]
            ),
        )
    elif query.data == "Music_play":
        query.message.edit_caption(f"* ✨ Bot play commands :-*"
            f"""
● /play <query> or <replied to audio>: play your searched music.
● /vplay <query> or <replied to video>: play your searched video.
● /search <query>: search your query on youtube.
● /lyrics <query>: search your song lyrics. 
● /replay <query> : play your query again.
● /queue : get your current playing and queued track for group.

☆✧....𝐁𝐘🫧 » [☄️𝐌ᴏᴏɴ🌙](https://t.me/About_ur_Moonshining/5)....🥀🥀✧☆

(✿◠‿◠)
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="• Back •", callback_data="Music_"),InlineKeyboardButton(text="Support", callback_data="mukesh_support")
                    ]
                ]
            ),
        )
    elif query.data == "Music_bot":
        query.message.edit_caption(f"* ✨ Bot developer commands :-*"
            f"""
● /activevc : get the active voice chat.
● /setpfp : set the pfp of music assitant.
● /delpfp : del the pfp of music assistant.
● /setbio : set the bio of music assistant.
● /setname : set the new name of assistant.
● /meval : something crazy u shouldn't know.

☆✧....𝐁𝐘🫧 » [☄️𝐌ᴏᴏɴ🌙](https://t.me/About_ur_Moonshining/5)....🥀🥀✧☆

(✿◠‿◠)
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=" • Back • ", callback_data="Music_"),InlineKeyboardButton(text="Support", callback_data="mukesh_support")
                    ]
                ]
            ),
        )
    elif query.data == "Music_extra":
        query.message.edit_caption(f"*» ᴇxᴛʀᴀ ᴄᴏᴍᴍᴀɴᴅꜱ «*"
            f"""
/start - ꜱᴛᴀʀᴛ ᴛʜᴇ ᴍᴜꜱɪᴄ ʙᴏᴛ.
/help  - ɢᴇᴛ ᴄᴏᴍᴍᴀɴᴅꜱ ʜᴇʟᴘᴇʀ ᴍᴇɴᴜ ᴡɪᴛʜ ᴅᴇᴛᴀɪʟᴇᴅ ᴇxᴘʟᴀɴᴀᴛɪᴏɴꜱ ᴏғ ᴄᴏᴍᴍᴀɴᴅꜱ.
/ping- ᴘɪɴɢ ᴛʜᴇ ʙᴏᴛ ᴀɴᴅ ᴄʜᴇᴄᴋ ʀᴀᴍ, ᴄᴘᴜ ᴇᴛᴄ ꜱᴛᴀᴛꜱ ᴏғ ʙᴏᴛ.
/animelogo - ᴇɴᴛᴇʀ ᴛᴇxᴛ ᴀғᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ɢᴇɴʀᴀᴛᴇ ᴀɴɪᴍᴇ ʟᴏɢᴏ.
/meme ➠ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ɢᴇɴʀᴀᴛᴇ ᴍᴇᴍᴇs.
/gmtag ➠ ғᴏʀ ᴍᴏʀɴɪɴɢ ᴡɪsʜᴇs🥰.
/gmstop  ➠ sᴛᴏᴘ ᴍᴏʀɴɪɴɢ ᴡɪsʜᴇs.
/gntag  ➠ ғᴏʀ ɴɪɢʜᴛ ᴡɪsʜᴇs 😴.
/gnstop  ➠ sᴛᴏᴘ ɴɪɢʜᴛ ᴡɪsʜᴇs😴.
/shayari   ➠ ᴛᴀɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs ᴡɪᴛʜ sʜᴀʏʀɪ😜.
/shayarioff  ➠ sᴛᴏᴘ ᴍᴇɴᴛɪᴏɴɪɴɢ sʜᴀʏʀɪ.
/wish ➠ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴡɪsʜ ᴀғᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.
/bored ➠ ᴊᴜsᴛ ғᴏʀ ғᴜɴ😁.
/gay ➠ ɢᴇᴛ ʏᴏᴜʀ ɢᴀʏ ᴘᴇʀᴄᴇɴᴛᴀɢᴇ  ˡᵒˡ 😅.
*ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ:*
/settings - ɢᴇᴛ a ᴄᴏᴍᴘʟᴇᴛᴇ ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ ᴡɪᴛʜ ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴꜱ

☆✧....𝐁𝐘🫧 » [☄️𝐌ᴏᴏɴ🌙](https://t.me/About_ur_Moonshining/5)....🥀🥀✧☆
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=" ʙᴀᴄᴋ ", callback_data="Music_"),InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", callback_data="mukesh_support")
                    ]
                ]
            ),
        )
    elif query.data == "Music_back":
        first_name = update.effective_user.first_name
        query.message.edit_caption(PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,

        )


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_photo(START_IMG,
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=" ʜᴇʟᴘ ​",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_photo("https://envs.sh/S_w.jpg","» Choose an way to get help from me ✨",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="• Open in private •",
                            url="https://t.me/{}?start=help".format(context.bot.username),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="• Open here •",
                            callback_data="Main_help",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="• Back •", callback_data="help_back"),InlineKeyboardButton(text="Support", callback_data="mukesh_support")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="◀",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text("""Hi there! There are quite a few settings for {} - go ahead and pick what "
                you're interested in.""".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(text=
                """Hi there! There are quite a few settings for {} - go ahead and pick what 
                you're interested in.""".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text("""Hi there! There are quite a few settings for {} - go ahead and pick what 
                you're interested in.""".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ᴛʜɪs ᴄʜᴀᴛ's sᴇᴛᴛɪɴɢs ᴀs ᴡᴇʟʟ ᴀs ʏᴏᴜʀs"
            msg.reply_photo(START_IMG,text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴇᴛᴛɪɴɢs​",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs"

    else:
        send_settings(chat.id, user.id, True)


def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 7297381612:
            update.effective_message.reply_text(
                f"» ᴛʜᴇ ᴅᴇᴠᴇʟᴏᴩᴇʀ ᴏғ {dispatcher.bot.first_name} sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ɪs [ɢɪᴛʜᴜʙ](https://t.me/pwmbothub)"
                f"\n\nʙᴜᴛ ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴅᴏɴᴀᴛᴇ ᴛᴏ ᴛʜᴇ ᴩᴇʀsᴏɴ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴜɴɴɪɴɢ ᴍᴇ : [ʜᴇʀᴇ]({DONATE_STRING})",
                parse_mode=ParseMode.MARKDOWN,
                
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                
            )

            update.effective_message.reply_text(
                "ɪ'ᴠᴇ ᴘᴍ'ᴇᴅ ʏᴏᴜ ᴀʙᴏᴜᴛ ᴅᴏɴᴀᴛɪɴɢ ᴛᴏ ᴍʏ ᴄʀᴇᴀᴛᴏʀ!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ғɪʀsᴛ ᴛᴏ ɢᴇᴛ ᴅᴏɴᴀᴛɪᴏɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():
    global x
    x=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="+ Add me to your clan darlo +",
                            url="https://t.me/Meowstericxbot?startgroup=true"
                            )
                       ]
                ]
                     )
    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                f"@{SUPPORT_CHAT}",
                photo=f"{START_IMG}",
                caption=f"""
✨ [Meowsteric bot 😺](https://t.me/Meowsterxbot) I am alive 🖤!

{BOT_NAME} system stats :

**✨  Uptime:** `{y()}`
**☁️  Ram:** `{telever}`
**❄️  Cpu:** `{tlhver}`
**🔮  Disk:** `{pyrover}`

Made [Meowsteric bot 😺](https://t.me/Meowsterxbot) with love by ᴅᴇᴠᴇʟᴏᴘᴇʀs✨🥀
""",reply_markup=x,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)
    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        Mukesh_about_callback, pattern=r"mukesh_", run_async=True
    )
    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )
    music_callback_handler = CallbackQueryHandler(
        Music_about_callback, pattern=r"Music_",run_async=True
    )
    moon_callback_handler = CallbackQueryHandler(
        Moon_about_callback, pattern=r"moon_", run_async=True
    )
    mukeshrobot_main_handler = CallbackQueryHandler(
        MukeshRobot_Main_Callback, pattern=r".*_help",run_async=True)
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(music_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)
    dispatcher.add_handler(mukeshrobot_main_handler)
    dispatcher.add_error_handler(error_callback)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(moon_callback_handler)
    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
