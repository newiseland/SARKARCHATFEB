import requests
import openai  # Install via: pip install openai
from MukeshAPI import api
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from nexichat import nexichat as app

# Set your OpenAI API key here
OPENAI_API_KEY = "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"

@Client.on_message(filters.command(["gemini", "ai", "ask", "chatgpt"]))
async def gemini_handler(client, message):
    if (
        message.text.startswith(f"/gemini@{client.me.username}")
        and len(message.text.split(" ", 1)) > 1
    ):
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        if len(message.command) > 1:
            user_input = " ".join(message.command[1:])
        else:
            await message.reply_text("ᴇxᴀᴍᴘʟᴇ :- `/ask who is Narendra Modi`")
            return

    try:
        response = api.gemini(user_input)
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        result = response.get("results")
        if result:
            await message.reply_text(result, quote=True)
            return
    except Exception as e:
        print(f"Gemini API Error: {e}")

    try:
        openai.api_key = OPENAI_API_KEY
        chat_response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" if you have a limited budget
            messages=[{"role": "user", "content": user_input}],
        )

        if chat_response and "choices" in chat_response:
            ai_reply = chat_response["choices"][0]["message"]["content"]
            await message.reply_text(ai_reply, quote=True)
            return
    except Exception as e:
        print(f"ChatGPT API Error: {e}")

    try:
        base_url = "https://chatwithai.codesearch.workers.dev/?chat="
        response = requests.get(base_url + user_input)
        if response and response.text.strip():
            await message.reply_text(response.text.strip(), quote=True)
        else:
            await message.reply_text("**All AI services are currently unavailable**")
    except Exception as e:
        print(f"Chat with AI Error: {e}")
        await message.reply_text("**ChatGPT is currently unavailable. Try again later.**")
