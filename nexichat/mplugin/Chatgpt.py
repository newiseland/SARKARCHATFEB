import requests
import logging
from MukeshAPI import api
from pyrogram import filters, Client
from pyrogram.enums import ChatAction

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize your bot with Pyrogram
app = Client("my_bot")

@app.on_message(filters.command(["gemini", "ask", "chatgpt"]))
async def gemini_handler(client, message):
    user_input = extract_user_input(client, message)
    
    if user_input is None:
        await message.reply_text("Example: /ask who is Narendra Modi")
        return

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        response = api.gemini(user_input)
        result = response.get("results")
        
        # Check API response and send result or fallback
        if result:
            await message.reply_text(result, quote=True)
        else:
            await fallback_response(user_input, message)
    except Exception as e:
        logging.error(f"Error with Gemini API: {e}")
        await fallback_response(user_input, message)

async def fallback_response(user_input, message):
    base_url = "https://chatwithai.codesearch.workers.dev/?chat="
    try:
        response = requests.get(base_url + user_input)
        
        if response.status_code == 200 and response.text.strip():
            await message.reply_text(response.text.strip(), quote=True)
        else:
            await message.reply_text("Both Gemini and Chat with AI are currently unavailable.")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        await message.reply_text("ChatGPT is currently down. Try again later.")

def extract_user_input(client, message):
    """
    Extracts user input from the message.
    Returns None if no valid input is provided.
    """
    if message.text.startswith(f"/gemini@{client.me.username}") and len(message.text.split(" ", 1)) > 1:
        return message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        return message.reply_to_message.text
    else:
        if len(message.command) > 1:
            return " ".join(message.command[1:])
    return None

if __name__ == "__main__":
    app.run()
