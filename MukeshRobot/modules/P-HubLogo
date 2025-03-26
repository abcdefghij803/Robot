import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from MukeshRobot import dispatcher, pbot

# Function to generate P-Hub logo as an image
def generate_phlogo_image(text1, text2):
    # Define image size and font
    img = Image.new('RGB', (300, 100), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load fonts (you need to specify a path to a font file, or adjust this as necessary)
    font = ImageFont.truetype("arial.ttf", 40)

    # Draw the text on the image
    draw.text((10, 25), text1, fill="white", font=font)
    draw.text((150, 25), text2, fill="orange", font=font)

    # Convert image to bytes
    bio = BytesIO()
    bio.name = 'phlogo.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

# /phlogo command handler (to generate logo as image)
def phlogo(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /phlogo <word1> <word2>")
        return
    
    text1, text2 = args[0], args[1]
    bio = generate_phlogo_image(text1, text2)
    update.message.reply_photo(photo=bio, caption=f"Here is your P-Hub logo for '{text1} {text2}'")

# /phst command handler (to generate logo as sticker)
def phst(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /phst <word1> <word2>")
        return

    text1, text2 = args[0], args[1]
    bio = generate_phlogo_image(text1, text2)
    update.message.reply_sticker(sticker=bio)

# /genpw command handler (to generate a random password)
def genpw(update: Update, context: CallbackContext):
    length = 12
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    update.message.reply_text(f"Here is your random password: `{password}`", parse_mode="Markdown")

# Main function to add handlers
def main():
    dispatcher.add_handler(CommandHandler('phlogo', phlogo))
    dispatcher.add_handler(CommandHandler('phst', phst))
    dispatcher.add_handler(CommandHandler('genpw', genpw))

    # Start the bot
    pbot.run()

if __name__ == "__main__":
    main()

__help__ = """
 » Available commands for P-Hub Logo 

● /phlogo <word1> <word2> : to generate logo as image.
● /phst <word1> <word2> : to generate logo as sticker.
● /genpw : to generate random password.

(✿◠‿◠)
 """

__mod_name__ = "P-Hub Logo"
