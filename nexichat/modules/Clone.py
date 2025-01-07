import logging
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.types import BotCommand
from config import API_HASH, API_ID, OWNER_ID
from nexichat import nexichat as app, save_clonebot_owner
from nexichat import db as mongodb

CLONES = set()
cloneownerdb = mongodb.cloneownerdb
clonebotdb = mongodb.clonebotdb

# Track pending approvals
pending_approvals = {}
approval_lock = asyncio.Lock()

@app.on_message(filters.command(["clone", "host", "deploy"]))
async def clone_txt(client, message):
    if len(message.command) > 1:
        bot_token = message.text.split("/clone", 1)[1].strip()
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        # Notify the owner for approval
        approval_message = await app.send_message(
            int(OWNER_ID),
            f"**#Clone_Request**\n\n"
            f"**Requester:** {username} (ID: {user_id})\n"
            f"**Bot Token:** `{bot_token}`\n\n"
            f"Approve this request by using `/approve {user_id}`.\n"
            f"Reject this request by using `/reject {user_id}`."
        )
        
        # Save the approval details
        async with approval_lock:
            pending_approvals[user_id] = {
                "message": message,
                "bot_token": bot_token,
                "approval_message_id": approval_message.id,
            }
        await message.reply_text("**Your request has been sent to the owner for approval. Please wait.**")
    else:
        await message.reply_text("**Provide Bot Token after /clone Command from @Botfather.**\n\n**Example:** `/clone bot token paste here`")

@app.on_message(filters.command("approve") & filters.user(int(OWNER_ID)))
async def approve_clone(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("**⚠️ Please provide the user ID to approve the clone request.**")
            return
        
        user_id = int(message.command[1])
        
        async with approval_lock:
            if user_id not in pending_approvals:
                await message.reply_text("**⚠️ No pending clone request found for this user ID.**")
                return
            
            approval_details = pending_approvals.pop(user_id)
        
        user_message = approval_details["message"]
        bot_token = approval_details["bot_token"]

        # Proceed with cloning
        await clone_bot(user_message, bot_token)
        
        # Notify the requester
        await user_message.reply_text("**Your clone request has been approved and is being processed.**")
        await message.reply_text(f"**✅ Clone request for user ID {user_id} has been approved.**")
        
        # Update the approval message
        await app.edit_message_text(
            int(OWNER_ID), approval_details["approval_message_id"], 
            "**✅ Clone request has been approved and processed.**"
        )
    except Exception as e:
        logging.exception(e)
        await message.reply_text(f"**An error occurred while approving the clone request:** {e}")

@app.on_message(filters.command("reject") & filters.user(int(OWNER_ID)))
async def reject_clone(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("**⚠️ Please provide the user ID to reject the clone request.**")
            return
        
        user_id = int(message.command[1])
        
        async with approval_lock:
            if user_id not in pending_approvals:
                await message.reply_text("**⚠️ No pending clone request found for this user ID.**")
                return
            
            approval_details = pending_approvals.pop(user_id)
        
        # Notify the requester
        await approval_details["message"].reply_text("**Your clone request has been rejected by the owner.**")
        await message.reply_text(f"**❌ Clone request for user ID {user_id} has been rejected.**")
        
        # Update the approval message
        await app.edit_message_text(
            int(OWNER_ID), approval_details["approval_message_id"], 
            "**❌ Clone request has been rejected by the owner.**"
        )
    except Exception as e:
        logging.exception(e)
        await message.reply_text(f"**An error occurred while rejecting the clone request:** {e}")

async def clone_bot(message, bot_token):
    mi = await message.reply_text("Please wait while I check the bot token.")
    try:
        ai = Client(bot_token, API_ID, API_HASH, bot_token=bot_token, plugins=dict(root="nexichat/mplugin"))
        await ai.start()
        bot = await ai.get_me()
        bot_id = bot.id
        user_id = message.from_user.id
        await save_clonebot_owner(bot_id, user_id)
        await ai.set_bot_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get the help menu"),
            BotCommand("clone", "Make your own chatbot"),
            BotCommand("ping", "Check if the bot is alive or dead"),
            BotCommand("lang", "Select bot reply language"),
            BotCommand("chatlang", "Get current using lang for chat"),
            BotCommand("resetlang", "Reset to default bot reply lang"),
            BotCommand("id", "Get users user_id"),
            BotCommand("stats", "Check bot stats"),
            BotCommand("gcast", "Broadcast any message to groups/users"),
            BotCommand("chatbot", "Enable or disable chatbot"),
            BotCommand("status", "Check chatbot enable or disable in chat"),
            BotCommand("shayri", "Get random shayri for love"),
            BotCommand("ask", "Ask anything from chatgpt"),
            BotCommand("repo", "Get chatbot source code"),
        ])
        
        details = {
            "bot_id": bot.id,
            "is_bot": True,
            "user_id": user_id,
            "name": bot.first_name,
            "token": bot_token,
            "username": bot.username,
        }
        await clonebotdb.insert_one(details)
        CLONES.add(bot.id)
        
        await mi.edit_text(
            f"**Bot @{bot.username} has been successfully cloned and started ✅.**\n"
            "**Remove clone by :- /delclone**\n"
            "**Check all cloned bot list by:- /cloned**"
        )
    except Exception as e:
        logging.exception(e)
        await mi.edit_text(f"**⚠️ Error:**\n\n`{e}`")

@app.on_message(filters.command("cloned"))
async def list_cloned_bots(client, message):
    try:
        cloned_bots = clonebotdb.find()
        cloned_bots_list = await cloned_bots.to_list(length=None)
        if not cloned_bots_list:
            await message.reply_text("No bots have been cloned yet.")
            return
        total_clones = len(cloned_bots_list)
        text = f"**Total Cloned Bots:** {total_clones}\n\n"
        for bot in cloned_bots_list:
            text += f"**Bot ID:** `{bot['bot_id']}`\n"
            text += f"**Bot Name:** {bot['name']}\n"
            text += f"**Bot Username:** @{bot['username']}\n\n"
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("**An error occurred while listing cloned bots.**")
