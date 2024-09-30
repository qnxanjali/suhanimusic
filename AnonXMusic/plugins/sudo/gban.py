from pyrogram import Client, filters
from AnonXMusic import app
from AnonXMusic.utils.extraction import extract_user
import asyncio
import logging
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils import get_readable_time
from AnonXMusic.utils.database import (
    add_banned_user,
    remove_banned_user,
    get_served_chats,
)
from config import BANNED_USERS
from pytz import timezone 
from datetime import timedelta, datetime

def get_readable_time(delta: timedelta) -> str:
    """Convert a timedelta object to a readable string."""
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

# Define authors, support chat ID and support channel ID
AUTHORS = [6260080241, 6681980705]
SUPPORT_CHAT_ID = -1001806995682

async def get_user_id(query):
    """Get user ID from username or directly if it's a numeric user ID."""
    if query.isnumeric():
        return int(query)
    try:
        user = await app.get_users(query)
        return user.id
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

async def send_request_message(user, reason, action, message):
    """Send a request message to the support chat for approval."""
    chat_name = message.chat.title if message.chat.title else "Private Chat"
    chat_id = message.chat.id
    ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
    utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # Get UTC time

    request_message = await app.send_message(
        SUPPORT_CHAT_ID,
        f"""<b>ᴀᴘᴘʀᴏᴠᴇ {action} ꜰᴏʀ ᴜꜱᴇʀ</b> :
{user.first_name}
<b>ᴜꜱᴇʀ ɪᴅ</b> : <code>{user.id}</code>

<b>ʀᴇQᴜᴇꜱᴛ ꜰʀᴏᴍ ᴄʜᴀᴛ ɪᴅ</b> : <code>{chat_id}</code>

<b>ʀᴇQᴜᴇꜱᴛ ꜰʀᴏᴍ ᴄʜᴀᴛ ɴᴀᴍᴇ</b> : {chat_name}

<b>ʀᴇᴀꜱᴏɴ</b> : {reason if reason else "No reason provided"}

<b>ʀᴇQᴜᴇꜱᴛ ʙʏ</b> : {message.from_user.first_name}

<b>ᴅᴀᴛᴇ & ᴛɪᴍᴇ : {ind_time}</b>
<b>ᴜɴɪᴠᴇʀꜱᴀʟ ᴛɪᴍᴇ</b> : {utc_time}

<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ : @TheAnjaliBot</b>
        """,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✯ ᴀᴘᴘʀᴏᴠᴇ ✯", callback_data=f"{action}_approve_{user.id}_{reason}")],
            [InlineKeyboardButton("✯ ᴅᴇᴄʟɪɴᴇ ✯", callback_data=f"{action}_decline_{user.id}_{reason}")]
        ])
    )
    return request_message

@app.on_message(filters.command(["gban", "globalban"]) & SUDOERS)
async def global_ban(_, message):
    reason = None
    user_id = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = message.reply_to_message.text
    else:
        msg_parts = message.text.split(None, 1)
        if len(msg_parts) > 1:
            user_query = msg_parts[1].split()[0]
            user_id = await get_user_id(user_query)
            reason = " ".join(msg_parts[1].split()[1:]) if len(msg_parts[1].split()) > 1 else None

    if user_id is None:
        await message.reply("Please specify a user ID, username, or reply to a message.")
        return

    user = await app.get_users(user_id)
    request_message = await send_request_message(user, reason, "Global_Ban", message)

    utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # Get UTC time

    response_message = f"""<b>ʏᴏᴜʀ ɢʟᴏʙᴀʟ ʙᴀɴ ʀᴇQᴜᴇꜱᴛ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇɴᴅᴇᴅ ᴛᴏ ᴛᴇᴀᴍ</b>

<b>ʀᴇQᴜᴇꜱᴛ ᴛᴏ ɢʟᴏʙᴀʟ ʙᴀɴ
ᴜꜱᴇʀ</b> : {user.first_name}

<b>ʀᴇᴀꜱᴏɴ</b> : {reason if reason else "No reason provided"}

<b>ʀᴇQᴜᴇꜱᴛ ʙʏ</b> : {message.from_user.first_name}

<b>ʏᴏᴜʀ ʀᴇQᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴄʜᴇᴄᴋᴇᴅ ᴀɴᴅ ɪꜰ ɪᴛ'ꜱ ɢᴇɴᴜɪɴᴇ ᴛʜᴇɴ ʙᴇ ꜱᴜʀᴇ ɪᴛ ᴡɪʟʟ ʙᴇ ᴀᴘᴘʀᴏᴠᴇᴅ.
ᴛʜᴀɴᴋꜱ ꜰᴏʀ ʏᴏᴜʀ ɢʟᴏʙᴀʟ ʙᴀɴ ʀᴇQᴜᴇꜱᴛ.

ᴄʜᴇᴄᴋ ᴍʏ ꜰᴜɴᴄᴛɪᴏɴꜱ ɪɴ ᴘʀɪᴠᴀᴛᴇ

ᴜɴɪᴠᴇʀꜱᴀʟ ᴛɪᴍᴇ</b> : <b>{utc_time}</b>

<b>ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ : @ANJALINETWORK</b>

<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ : @TheAnjaliBot</b>"""

    await message.reply(response_message)
    await message.delete()

@app.on_message(filters.command(["ungban"]) & SUDOERS)
async def global_ungban(_, message):
    reason = None
    user_id = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = message.reply_to_message.text
    else:
        msg_parts = message.text.split(None, 1)
        if len(msg_parts) > 1:
            user_query = msg_parts[1].split()[0]
            user_id = await get_user_id(user_query)
            reason = " ".join(msg_parts[1].split()[1:]) if len(msg_parts[1].split()) > 1 else None

    if user_id is None:
        await message.reply("Please specify a user ID, username, or reply to a message.")
        return

    user = await app.get_users(user_id)
    request_message = await send_request_message(user, reason, "Global_Unban", message)

    utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # Get UTC time

    response_message = f"""<b>ʏᴏᴜʀ ɢʟᴏʙᴀʟ ᴜɴʙᴀɴ ʀᴇQᴜᴇꜱᴛ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇɴᴅᴇᴅ ᴛᴏ ᴛᴇᴀᴍ</b>

<b>ʀᴇQᴜᴇꜱᴛ ᴛᴏ ɢʟᴏʙᴀʟ ᴜɴʙᴀɴ
ᴜꜱᴇʀ :</b> {user.first_name}

<b>ʀᴇᴀꜱᴏɴ :</b> {reason if reason else "No reason provided"}

<b>ʀᴇQᴜᴇꜱᴛ ʙʏ :</b> {message.from_user.first_name}

<b>ʏᴏᴜʀ ʀᴇQᴜᴇꜱᴛ ᴡɪʟʟ ʙᴇ ᴄʜᴇᴄᴋᴇᴅ ᴀɴᴅ ɪꜰ ɪᴛ'ꜱ ɢᴇɴᴜɪɴᴇ ᴛʜᴇɴ ʙᴇ ꜱᴜʀᴇ ɪᴛ ᴡɪʟʟ ʙᴇ ᴀᴘᴘʀᴏᴠᴇᴅ.
ᴛʜᴀɴᴋꜱ ꜰᴏʀ ʏᴏᴜʀ ɢʟᴏʙᴀʟ ᴜɴʙᴀɴ ʀᴇQᴜᴇꜱᴛ.

ᴄʜᴇᴄᴋ ᴍʏ ꜰᴜɴᴄᴛɪᴏɴꜱ ɪɴ ᴘʀɪᴠᴀᴛᴇ.</b>

<b>ᴜɴɪᴠᴇʀꜱᴀʟ ᴛɪᴍᴇ :</b> {utc_time}

<b>ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ : @ANJALINETWORK</b>

<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ : @TheAnjaliBot</b>"""

    await message.reply(response_message)
    await message.delete()

@app.on_callback_query(filters.regex(r'^Global_(Ban|Unban)_(approve|decline)_(\d+)_(.*)$'))
async def handle_global_action_callback(client: Client, query: CallbackQuery):
    try:
        # Extract action, status, user_id, and reason from the callback data
        data_parts = query.data.split("_")
        if len(data_parts) != 5:
            raise ValueError("Callback data format is incorrect")

        action = data_parts[1]
        status = data_parts[2]
        user_id_str = data_parts[3]
        user_id = int(user_id_str)
        reason = "_".join(data_parts[4:])  # Join all remaining parts as the reason

    except ValueError as e:
        print(f"Error parsing callback data: {e}")
        await query.answer("Failed to process request. Please try again.", show_alert=True)
        # Always try to delete the message in case of error
        try:
            await query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
        return

    if query.from_user.id not in AUTHORS:
        await query.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴜᴛʜᴏʀ", show_alert=True)
        # Do not delete the message if the user is unauthorized
        return

    # Record approval author
    approval_author = query.from_user.first_name

    # Process the approval or decline action only if the user is an author
    try:
        # Send notification message about the approval/decline
        if status == "approve":
            if action == "Ban":
                await query.answer("ɢʟᴏʙᴀʟ ʙᴀɴ ᴀᴘᴘʀᴏᴠᴇᴅ.", show_alert=True)
                # Run the global ban action in the background
                asyncio.create_task(global_ban_action(user_id, query.message, approval_author, reason))
            elif action == "Unban":
                await query.answer("ɢʟᴏʙᴀʟ ᴜɴʙᴀɴ ᴀᴘᴘʀᴏᴠᴇᴅ.", show_alert=True)
                # Run the global unban action in the background
                asyncio.create_task(global_ungban_action(user_id, query.message, approval_author, reason))
        elif status == "decline":
            if action == "Ban":
                await query.answer("ɢʟᴏʙᴀʟ ʙᴀɴ ᴅᴇᴄʟɪɴᴇᴅ.", show_alert=True)
            elif action == "Unban":
                await query.answer("ɢʟᴏʙᴀʟ ᴜɴʙᴀɴ ᴅᴇᴄʟɪɴᴇᴅ.", show_alert=True)

        # Delete the original callback message
        try:
            await query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")

        # Send notification about the action taken
        notification_message = await app.send_message(
            SUPPORT_CHAT_ID,
            f"{action} ʀᴇQᴜᴇꜱᴛ {status} ʙʏ {approval_author}.",
        )

        # Delete the notification message after 15 seconds
        await asyncio.sleep(15)
        try:
            await notification_message.delete()
        except Exception as e:
            print(f"Failed to delete notification message: {e}")

    except Exception as e:
        # Handle any unexpected exceptions
        print(f"Unexpected error: {e}")
        await query.answer("An unexpected error occurred. Please try again.", show_alert=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def send_flood_wait_message(flood_wait_duration, operation_name, chat_id):
    """Send a message to the support chat when a flood wait occurs."""
    message = (f"Flood wait required for {operation_name} operation in chat {chat_id}.\n"
               f"Duration: {flood_wait_duration} seconds.")
    await app.send_message(SUPPORT_CHAT_ID, message)
    logging.info(f"Sent flood wait message: {message}")

async def global_ban_action(user_id, message, approval_author, reason):
    """Perform the global ban action."""
    user = await app.get_users(user_id)
    number_of_chats = 0
    served_chats = [int(chat["chat_id"]) for chat in await get_served_chats()]
    start_time = datetime.utcnow()

    # Ban in main client
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, user_id)
            number_of_chats += 1
        except FloodWait as fw:
            await send_flood_wait_message(fw.value, "ban", chat_id)
            await asyncio.sleep(int(fw.value))
        except Exception as e:
            logging.error(f"Failed to ban user {user_id} in chat {chat_id}: {e}")
        await asyncio.sleep(1)  # Delay to prevent hitting API limits

    end_time = datetime.utcnow()
    time_taken = end_time - start_time

    final_message = f"""#ɴᴇᴡ_ᴜꜱᴇʀ_ɢʙᴀɴ

<b>ɢʟᴏʙᴀʟ ʙᴀɴ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.

<b>ᴜꜱᴇʀ :</b> {user.first_name}
<b>ᴜꜱᴇʀ ɪᴅ :</b> <code>{user.id}</code>

<b>ʀᴇᴀꜱᴏɴ :</b> {reason}

<b>ᴍᴀɴᴀɢᴇᴅ ʙʏ :</b> {message.from_user.first_name}
<b>ᴀᴘᴘʀᴏᴠᴇᴅ ʙʏ :</b> {approval_author}

<b>ɢʙᴀɴɴᴇᴅ ᴄʜᴀᴛꜱ :</b> {number_of_chats}

<b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ :</b> {get_readable_time(time_taken)}

<b>ᴜɴɪᴠᴇʀꜱᴀʟ ᴛɪᴍᴇ :</b>  {end_time.strftime('%Y-%m-%d %H:%M:%S')}

<b>ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ : @ANJALINETWORK</b>

<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ : @TheAnjaliBot</b>"""

    await app.send_message(SUPPORT_CHAT_ID, final_message)
    await add_banned_user(user.id)

async def global_ungban_action(user_id, message, approval_author, reason):
    """Perform the global unban action."""
    user = await app.get_users(user_id)
    number_of_chats = 0
    served_chats = [int(chat["chat_id"]) for chat in await get_served_chats()]
    start_time = datetime.utcnow()

    # Unban in main client
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, user_id)
            number_of_chats += 1
        except FloodWait as fw:
            await send_flood_wait_message(fw.value, "unban", chat_id)
            await asyncio.sleep(int(fw.value))
        except Exception as e:
            logging.error(f"Failed to unban user {user_id} in chat {chat_id}: {e}")
        await asyncio.sleep(1)  # Delay to prevent hitting API limits

    end_time = datetime.utcnow()
    time_taken = end_time - start_time

    final_message = f"""#ɴᴇᴡ_ᴜꜱᴇʀ_ᴜɴɢʙᴀɴ

<b>ɢʟᴏʙᴀʟ ᴜɴʙᴀɴ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.

<b>ᴜꜱᴇʀ :</b>  {user.first_name}
<b>ᴜꜱᴇʀ ɪᴅ :</b> <code>{user.id}</code>

<b>ʀᴇᴀꜱᴏɴ :</b> {reason}

<b>ᴍᴀɴᴀɢᴇᴅ ʙʏ :</b> {message.from_user.first_name}
<b>ᴀᴘᴘʀᴏᴠᴇᴅ ʙʏ :</b> {approval_author}

<b>ᴜɴɢʙᴀɴɴᴇᴅ ᴄʜᴀᴛꜱ :</b> {number_of_chats}

<b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ :</b> {get_readable_time(time_taken)}

<b>ᴜɴɪᴠᴇʀꜱᴀʟ ᴛɪᴍᴇ :</b> {end_time.strftime('%Y-%m-%d %H:%M:%S')}

<b>ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ : @ANJALINETWORK</b>

<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ : @TheAnjaliBot</b>"""

    await app.send_message(SUPPORT_CHAT_ID, final_message)
    await remove_banned_user(user.id)
