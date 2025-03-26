import html
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html

from MukeshRobot import DRAGONS, dispatcher
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.admin_rights import user_can_changeinfo
from MukeshRobot.modules.helper_funcs.alternate import send_message
from MukeshRobot.modules.helper_funcs.chat_status import (
    ADMIN_CACHE,
    bot_admin,
    can_pin,
    connection_status,
    user_admin,
can_promote
)
#from MukeshRobot.utils.admins import can_promote
from MukeshRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from MukeshRobot.modules.log_channel import loggable


@bot_admin
@user_admin
def set_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not user_can_changeinfo(chat, user, context.bot.id):
        return msg.reply_text(
            "» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ!"
        )

    if msg.reply_to_message and msg.reply_to_message.sticker:
        stkr_set_name = msg.reply_to_message.sticker.set_name
        if not stkr_set_name:
            return msg.reply_text("» ᴛʜɪs sᴛɪᴄᴋᴇʀ ᴅᴏᴇs ɴᴏᴛ ʙᴇʟᴏɴɢ ᴛᴏ ᴀɴʏ sᴛɪᴄᴋᴇʀ sᴇᴛ!")

        try:
            context.bot.set_chat_sticker_set(chat.id, stkr_set_name)
            msg.reply_text(f"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ɢʀᴏᴜᴩ sᴛɪᴄᴋᴇʀs ɪɴ {chat.title}!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "» ʏᴏᴜʀ ɢʀᴏᴜᴩ ɴᴇᴇᴅs ᴍɪɴɪᴍᴜᴍ 100 ᴍᴇᴍʙᴇʀs ᴛᴏ sᴇᴛ ᴀ sᴛɪᴄᴋᴇʀ ᴩᴀᴄᴋ!"
                )
            msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}.")
    else:
        msg.reply_text("» ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴠᴀʟɪᴅ sᴛɪᴄᴋᴇʀ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɢʀᴏᴜᴩ sᴛɪᴄᴋᴇʀ ᴩᴀᴄᴋ!")


@bot_admin
@user_admin
def setchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if not user_can_changeinfo(chat, user, context.bot.id):
        return msg.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ!")

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_name = msg.reply_to_message.document.file_name.lower()
            if file_name.endswith((".jpg", ".jpeg", ".png")):
                pic_id = msg.reply_to_message.document.file_id
            else:
                return msg.reply_text("» ᴏɴʟʏ .jpg, .jpeg, ᴀɴᴅ .png ғɪʟᴇs ᴀʀᴇ sᴜᴘᴘᴏʀᴛᴇᴅ ғᴏʀ ɢʀᴏᴜᴩ ᴩʀᴏғɪʟᴇ ᴩɪᴄ!")
        else:
            return msg.reply_text("» ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ sᴇᴛ ᴩʜᴏᴛᴏs ᴀs ɢʀᴏᴜᴩ ᴩғᴩ!")

        dlmsg = msg.reply_text("» ᴄʜᴀɴɢɪɴɢ ɢʀᴏᴜᴩ's ᴩʀᴏғɪʟᴇ ᴩɪᴄ...")
        tpic = context.bot.get_file(pic_id)
        
        try:
            tpic.download("gpic.png")
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(chat.id, photo=chatp)
            msg.reply_text("» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ɢʀᴏᴜᴩ ᴩʀᴏғɪʟᴇ ᴩɪᴄ!")
        except BadRequest as excp:
            msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.exists("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("» ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴠᴀʟɪᴅ ᴩʜᴏᴛᴏ ᴏʀ .jpg/.png ғɪʟᴇ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɢʀᴏᴜᴩ ᴩʀᴏғɪʟᴇ ᴩɪᴄ!")


@bot_admin
@user_admin
def rmchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if not user_can_changeinfo(chat, user, context.bot.id):
        return msg.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ!")

    try:
        context.bot.delete_chat_photo(chat.id)
        msg.reply_text("» sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ɢʀᴏᴜᴩ's ᴩʀᴏғɪʟᴇ ᴩɪᴄ!")
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}.")


@bot_admin
@user_admin
def set_desc(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not user_can_changeinfo(chat, user, context.bot.id):
        return msg.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ!")

    desc = msg.text.partition(" ")[2].strip()
    
    if not desc:
        return msg.reply_text("» ᴡᴛғ, ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇᴛ ᴀɴ ᴇᴍᴩᴛʏ ᴅᴇsᴄʀɪᴩᴛɪᴏɴ!")

    if len(desc) > 255:
        return msg.reply_text("» ᴅᴇsᴄʀɪᴩᴛɪᴏɴ ᴍᴜsᴛ ʙᴇ ʟᴇss ᴛʜᴀɴ 255 ᴄʜᴀʀᴀᴄᴛᴇʀs!")

    try:
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴩᴅᴀᴛᴇᴅ ᴄʜᴀᴛ ᴅᴇsᴄʀɪᴩᴛɪᴏɴ ɪɴ {chat.title}!")
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}.")

@bot_admin
@user_admin
def setchat_title(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if not user_can_changeinfo(chat, user, context.bot.id):
        return msg.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴩ ɪɴғᴏ!")

    title = " ".join(args).strip()

    if not title:
        return msg.reply_text("» ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɴᴇᴡ ᴄʜᴀᴛ ᴛɪᴛʟᴇ!")

    if len(title) > 255:
        return msg.reply_text("» ᴄʜᴀᴛ ᴛɪᴛʟᴇ ᴍᴜsᴛ ʙᴇ ʟᴇss ᴛʜᴀɴ 255 ᴄʜᴀʀᴀᴄᴛᴇʀs!")

    try:
        context.bot.set_chat_title(chat.id, title)
        msg.reply_text(
            f"» sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ <b>{title}</b> ᴀs ɴᴇᴡ ᴄʜᴀᴛ ᴛɪᴛʟᴇ!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}.")


@connection_status
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    # Check if the user has the right permissions
    if not (promoter.can_promote_members or promoter.status == "creator") and user.id not in DRAGONS:
        message.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴀᴅᴅ ɴᴇᴡ ᴀᴅᴍɪɴs !")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text("» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ's ᴛʜᴀᴛ ᴜsᴇʀ, ɴᴇᴠᴇʀ sᴇᴇɴ ʜɪᴍ ʙᴇғᴏʀᴇ !")
        return

    # Get the user to be promoted
    try:
        user_member = chat.get_member(user_id)
    except BadRequest:
        message.reply_text("» ᴜɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴜsᴇʀ ɪɴғᴏ. ᴍᴀʏʙᴇ ᴛʜᴇ ᴜsᴇʀ ɪs ɴᴏᴛ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.")
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ!")
        return

    if user_id == bot.id:
        message.reply_text("» ɪ ᴄᴀɴ'ᴛ ᴩʀᴏᴍᴏᴛᴇ ᴍʏsᴇʟғ!")
        return

    # Get bot's current permissions
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if "User_not_mutual_contact" in err.message:
            message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ᴘʀᴇsᴇɴᴛ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!")
        else:
            message.reply_text(f"» ᴇʀʀᴏʀ: {err.message}")
        return

    # Send confirmation message
    bot.sendMessage(
        chat.id,
        f"<b>» ᴩʀᴏᴍᴏᴛɪɴɢ ᴀ ᴜsᴇʀ ɪɴ</b> {chat.title}\n\n"
        f"ᴩʀᴏᴍᴏᴛᴇᴅ : {mention_html(user_member.user.id, user_member.user.first_name)}\n"
        f"ᴩʀᴏᴍᴏᴛᴇʀ : {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    # Log message for admin logs
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ᴩʀᴏᴍᴏᴛᴇᴅ\n"
        f"<b>ᴩʀᴏᴍᴏᴛᴇʀ :</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴇʀ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def lowpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    # Check if the user has promotion permissions
    if not (promoter.can_promote_members or promoter.status == "creator") and user.id not in DRAGONS:
        message.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴀᴅᴅ ɴᴇᴡ ᴀᴅᴍɪɴs !")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text("» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ's ᴛʜᴀᴛ ᴜsᴇʀ, ɴᴇᴠᴇʀ sᴇᴇɴ ʜɪᴍ ʙᴇғᴏʀᴇ !")
        return

    # Get the user to be promoted
    try:
        user_member = chat.get_member(user_id)
    except BadRequest:
        message.reply_text("» ᴜɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴜsᴇʀ ɪɴғᴏ. ᴍᴀʏʙᴇ ᴛʜᴇ ᴜsᴇʀ ɪs ɴᴏᴛ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.")
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ!")
        return

    if user_id == bot.id:
        message.reply_text("» ɪ ᴄᴀɴ'ᴛ ᴩʀᴏᴍᴏᴛᴇ ᴍʏsᴇʟғ!")
        return

    # Get bot's current permissions
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if "User_not_mutual_contact" in err.message:
            message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ᴘʀᴇsᴇɴᴛ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!")
        else:
            message.reply_text(f"» ᴇʀʀᴏʀ: {err.message}")
        return

    # Send confirmation message
    bot.sendMessage(
        chat.id,
        f"<b>» ʟᴏᴡ ᴩʀᴏᴍᴏᴛɪɴɢ ᴀ ᴜsᴇʀ ɪɴ </b>{chat.title}\n\n"
        f"<b>ᴩʀᴏᴍᴏᴛᴇᴅ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}\n"
        f"ᴩʀᴏᴍᴏᴛᴇʀ : {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    # Log message for admin logs
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ʟᴏᴡᴩʀᴏᴍᴏᴛᴇᴅ\n"
        f"<b>ᴩʀᴏᴍᴏᴛᴇʀ :</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴇʀ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message

@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def fullpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    # Check if the user has permission to promote admins
    if not (promoter.can_promote_members or promoter.status == "creator") and user.id not in DRAGONS:
        message.reply_text("» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ ᴀɴʏᴏɴᴇ !")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text("» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ's ᴛʜᴀᴛ ᴜsᴇʀ, ɪ ʜᴀᴠᴇ ɴᴇᴠᴇʀ sᴇᴇɴ ᴛʜᴇᴍ ʙᴇғᴏʀᴇ !")
        return

    # Fetch the user to be promoted
    try:
        user_member = chat.get_member(user_id)
    except BadRequest:
        message.reply_text("» ᴄᴀɴ'ᴛ ғᴇᴛᴄʜ ᴜsᴇʀ ᴅᴇᴛᴀɪʟs. ᴍᴀʏʙᴇ ᴛʜᴇʏ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.")
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ ʜᴇʀᴇ !")
        return

    if user_id == bot.id:
        message.reply_text("» ɪ ᴄᴀɴ'ᴛ ᴩʀᴏᴍᴏᴛᴇ ᴍʏsᴇʟғ!")
        return

    # Fetch bot's current permissions
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
    except BadRequest as err:
        if "User_not_mutual_contact" in err.message:
            message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ᴘʀᴇsᴇɴᴛ ɪɴ ᴛʜɪs ᴄʜᴀᴛ!")
        else:
            message.reply_text(f"» ᴇʀʀᴏʀ: {err.message}")
        return

    # Send confirmation message
    bot.sendMessage(
        chat.id,
        f"» ғᴜʟʟ ᴩʀᴏᴍᴏᴛɪɴɢ ᴀ ᴜsᴇʀ ɪɴ <b>{chat.title}</b>\n\n"
        f"<b>ᴜsᴇʀ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}\n"
        f"<b>ᴩʀᴏᴍᴏᴛᴇʀ :</b> {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    # Log message for admin logs
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ғᴜʟʟᴩʀᴏᴍᴏᴛᴇᴅ\n"
        f"<b>ᴩʀᴏᴍᴏᴛᴇʀ :</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴇʀ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message

@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    
    if not user_id:
        message.reply_text("» ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ ᴛʜᴀᴛ ᴜsᴇʀ ɪs, ᴘʟᴇᴀsᴇ ᴍᴇɴᴛɪᴏɴ ᴛʜᴇᴍ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
        return

    try:
        user_member = chat.get_member(user_id)
    except BadRequest:
        message.reply_text("» ᴜɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴜsᴇʀ ᴅᴇᴛᴀɪʟs. ᴍᴀʏʙᴇ ᴛʜᴇʏ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.")
        return

    if user_member.status == "creator":
        message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴛʜᴇ ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ. ɪ ᴄᴀɴ'ᴛ ᴅᴇᴍᴏᴛᴇ ᴛʜᴇᴍ.")
        return

    if user_member.status != "administrator":
        message.reply_text("» ᴛʜᴀᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ.")
        return

    if user_id == bot.id:
        message.reply_text("» ɪ ᴄᴀɴ'ᴛ ᴅᴇᴍᴏᴛᴇ ᴍʏsᴇʟғ, ʙᴜᴛ ɪғ ʏᴏᴜ ᴡᴀɴᴛ, ɪ ᴄᴀɴ ʟᴇᴀᴠᴇ.")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )

        bot.sendMessage(
            chat.id,
            f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇᴍᴏᴛᴇᴅ ᴀ ɴᴏᴡ ғᴏʀᴍᴇʀ ᴀᴅᴍɪɴ ɪɴ <b>{chat.title}</b>\n\n"
            f"<b>ᴅᴇᴍᴏᴛᴇᴅ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}\n"
            f"<b>ᴅᴇᴍᴏᴛᴇʀ :</b> {mention_html(user.id, user.first_name)}",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#ᴅᴇᴍᴏᴛᴇᴅ\n"
            f"<b>ᴅᴇᴍᴏᴛᴇʀ :</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ᴅᴇᴍᴏᴛᴇᴅ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest as err:
        message.reply_text(f"» ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴇᴍᴏᴛᴇ: {err.message}")
        return


@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)


@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    # Extract user and title
    user_id, title = extract_user_and_text(message, args)
    
    if not user_id:
        message.reply_text("» I don't know who that user is, please mention them or use a valid user ID.")
        return

    try:
        user_member = chat.get_member(user_id)
    except BadRequest:
        message.reply_text("» Unable to fetch user details. Maybe they are not in this chat.")
        return

    # Bot खुद का title सेट नहीं कर सकता
    if user_id == bot.id:
        message.reply_text("» I can't set a title for myself.")
        return

    # केवल एडमिन्स के लिए Title सेट किया जा सकता है
    if user_member.status == "creator":
        message.reply_text("» That user is the owner of the chat. I can't change their title.")
        return

    if user_member.status != "administrator":
        message.reply_text("» I can only set titles for admins!")
        return

    # Title Blank नहीं हो सकता
    if not title:
        message.reply_text("» You can't set a blank title!")
        return

    # Title 16 characters से ज्यादा नहीं हो सकता
    if len(title) > 16:
        title = title[:16]  # Truncate to 16 characters
        message.reply_text("» The title was too long, it has been truncated to 16 characters.")

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
        bot.sendMessage(
            chat.id,
            f"» Successfully set title for <b>{html.escape(user_member.user.first_name)}</b> "
            f"to <b>{html.escape(title)}</b>!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as err:
        message.reply_text(f"» Failed to set title: {err}")

@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message is None:
        msg.reply_text("» ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴩɪɴ ɪᴛ !")
        return

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
            msg.reply_text(
                f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴩɪɴɴᴇᴅ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ.\nᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ᴍᴇssᴀɢᴇ.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ᴍᴇssᴀɢᴇ", url=f"{message_link}")]]
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ᴩɪɴɴᴇᴅ-ᴀ-ᴍᴇssᴀɢᴇ\n"
            f"<b>ᴩɪɴɴᴇᴅ ʙʏ :</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(
            "» ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴩɪɴ/ᴜɴᴩɪɴ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ !"
        )
        return

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id, prev_message.message_id)
            msg.reply_text(
                f"» sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴᴩɪɴɴᴇᴅ <a href='{message_link}'> ᴛʜɪs ᴩɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ</a>.",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

    if not prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id)
            msg.reply_text("» sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴᴩɪɴɴᴇᴅ ᴛʜᴇ ʟᴀsᴛ ᴩɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ.")
        except BadRequest as excp:
            if excp.message == "Message to unpin not found":
                msg.reply_text(
                    "» ɪ ᴄᴀɴ'ᴛ ᴜɴᴩɪɴ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ, ᴍᴀʏʙᴇ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ ɪs ᴛᴏᴏ ᴏʟᴅ ᴏʀ ᴍᴀʏʙᴇ sᴏᴍᴇᴏɴᴇ ᴀʟʀᴇᴀᴅʏ ᴜɴᴩɪɴɴᴇᴅ ɪᴛ."
                )
            else:
                raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"ᴜɴᴩɪɴɴᴇᴅ-ᴀ-ᴍᴇssᴀɢᴇ\n"
        f"<b>ᴜɴᴩɪɴɴᴇᴅ ʙʏ :</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@bot_admin
def pinned(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    msg = update.effective_message
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )

    chat = bot.getChat(chat_id=msg.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.message_id
        if msg.chat.username:
            link_chat_id = msg.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(msg.chat.id)).startswith("-100"):
            link_chat_id = (str(msg.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        msg.reply_text(
            f"ᴩɪɴɴᴇᴅ ᴏɴ {html.escape(chat.title)}.",
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴍᴇssᴀɢᴇ",
                            url=f"https://t.me/{link_chat_id}/{pinned_id}",
                        )
                    ]
                ]
            ),
        )

    else:
        msg.reply_text(
            f"» ᴛʜᴇʀᴇ's ɴᴏ ᴩɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ ɪɴ <b>{html.escape(chat.title)}!</b>",
            parse_mode=ParseMode.HTML,
        )


@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴩᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴀᴄᴄᴇss ɪɴᴠɪᴛᴇ ʟɪɴᴋs !",
            )
    else:
        update.effective_message.reply_text(
            "» ɪ ᴄᴀɴ ᴏɴʟʏ ɢɪᴠᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋs ғᴏʀ ɢʀᴏᴜᴩs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs !",
        )


@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat] -> unused variable
    user = update.effective_user  # type: Optional[User]
    args = context.args  # -> unused variable
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(
            update.effective_message,
            "» ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ɪɴ ɢʀᴏᴜᴩ's ɴᴏᴛ ɪɴ ᴩᴍ.",
        )
        return

    update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title  # -> unused variable

    try:
        msg = update.effective_message.reply_text(
            "» ғᴇᴛᴄʜɪɴɢ ᴀᴅᴍɪɴs ʟɪsᴛ...",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "» ғᴇᴛᴄʜɪɴɢ ᴀᴅᴍɪɴs ʟɪsᴛ...",
            quote=False,
            parse_mode=ParseMode.HTML,
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "ᴀᴅᴍɪɴs ɪɴ <b>{}</b>:".format(html.escape(update.effective_chat.title))

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )

        if user.is_bot:
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 🥀 ᴏᴡɴᴇʀ :"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n💫 ᴀᴅᴍɪɴs :"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0],
                html.escape(admin_group),
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🔮 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


__help__ = """
» Available commands for Admins 

User Commands:
● /admins: list of admins in the chat
● /pinned: to get the current pinned message.

Admins only:
● /pin: silently pins the message replied to - add 'loud' or 'notify' to give notifs to users
● /unpin: unpins the currently pinned message
● /invitelink: gets invite link
● /promote: promotes the user replied to
● /lowpromote: promotes the user replied to with half rights
● /fullpromote: promotes the user replied to with full rights
● /demote: demotes the user replied to
● /title <title here>: sets a custom title for an admin that the bot promoted
● /admincache: force refresh the admins list
● /del: deletes the message you replied to
● /purge: deletes all messages between this and the replied to message.
● /purge <integer X>*:* deletes the replied message, and X messages following it if replied to a message.
● /setgtitle <text>*:* set group title
● /setgpic*:* reply to an image to set as group photo
● /setdesc*:* Set group description
● /setsticker*:* Set group sticker
/⁠ᐠ⁠｡⁠ꞈ⁠｡⁠ᐟ⁠\
"""

SET_DESC_HANDLER = CommandHandler("setdesc", set_desc, run_async=True)
SET_STICKER_HANDLER = CommandHandler("setsticker", set_sticker, run_async=True)
SETCHATPIC_HANDLER = CommandHandler("setgpic", setchatpic, run_async=True)
RMCHATPIC_HANDLER = CommandHandler("delgpic", rmchatpic, run_async=True)
SETCHAT_TITLE_HANDLER = CommandHandler("setgtitle", setchat_title, run_async=True)

ADMINLIST_HANDLER = DisableAbleCommandHandler(
    ["admins", "staff"], adminlist, run_async=True
)

PIN_HANDLER = CommandHandler("pin", pin, run_async=True)
UNPIN_HANDLER = CommandHandler("unpin", unpin, run_async=True)
PINNED_HANDLER = CommandHandler("pinned", pinned, run_async=True)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite, run_async=True)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote, run_async=True)
FULLPROMOTE_HANDLER = DisableAbleCommandHandler(
    "fullpromote", fullpromote, run_async=True
)
LOW_PROMOTE_HANDLER = DisableAbleCommandHandler(
    "lowpromote", lowpromote, run_async=True
)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote, run_async=True)

SET_TITLE_HANDLER = CommandHandler("title", set_title, run_async=True)
ADMIN_REFRESH_HANDLER = CommandHandler(
    ["admincache", "reload", "refresh"],
    refresh_admin,
    run_async=True,
)

dispatcher.add_handler(SET_DESC_HANDLER)
dispatcher.add_handler(SET_STICKER_HANDLER)
dispatcher.add_handler(SETCHATPIC_HANDLER)
dispatcher.add_handler(RMCHATPIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(PINNED_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(FULLPROMOTE_HANDLER)
dispatcher.add_handler(LOW_PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "Admins"
__command_list__ = [
    "setdesc" "setsticker" "setgpic" "delgpic" "setgtitle" "adminlist",
    "admins",
    "invitelink",
    "promote",
    "fullpromote",
    "lowpromote",
    "demote",
    "admincache",
]
__handlers__ = [
    SET_DESC_HANDLER,
    SET_STICKER_HANDLER,
    SETCHATPIC_HANDLER,
    RMCHATPIC_HANDLER,
    SETCHAT_TITLE_HANDLER,
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    PINNED_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    FULLPROMOTE_HANDLER,
    LOW_PROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
