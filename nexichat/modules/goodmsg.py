import re
import random
from pyrogram import filters
from nexichat import nexichat  # Assuming this is where the bot is defined

@nexichat.on_message(filters.command(["gm", "goodmorning", "good morning"], prefixes=["/", "g", "G"]))
async def goodmorning_command_handler(_, message):
    sender = message.from_user.mention
    send_sticker = random.choice([True, False])
    
    if send_sticker:
        sticker_id = get_random_sticker()
        app.send_sticker(message.chat.id, sticker_id)
        message.reply_text(f"❖ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ❖ ᴡɪsʜɪɴɢ ʏᴏᴜ ᴀ ʙʟɪssғᴜʟ ᴅᴀʏ ❖\n\n❍  {sender} 🌞 \n\n❖ ɢᴏ ᴏᴜᴛ ᴀɴᴅ ᴇxᴘʟᴏʀᴇ!")
    else:
        emoji = get_random_emoji()
        app.send_message(message.chat.id, emoji)
        message.reply_text(f"❖ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ❖ ᴡɪsʜɪɴɢ ʏᴏᴜ ᴀ ʙʟɪssғᴜʟ ᴅᴀʏ ❖\n\n❍  {sender} {emoji} \n\n❖ ɢᴏ ᴏᴜᴛ ᴀɴᴅ ᴇxᴘʟᴏʀᴇ!")

async def get_random_sticker():
    stickers = [
        "CAACAgUAAxkBAAJWlmd-o5UiztU-0UFo5si8Zxqz9HQDAAKCEAAC_k_4V3tFbOFsrqp_HgQ", # Sticker 1
    ]
    return random.choice(stickers)

async def get_random_emoji():
    emojis = [
        "🌅",  # Sun emoji for Good Morning
        "☀️",  # Sun emoji for Good Morning
        "🌞",  # Sun with face emoji
    ]
    return random.choice(emojis)
