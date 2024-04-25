import logging
from telethon import TelegramClient, events, Button
import ast

logging.basicConfig(format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.INFO)
log = logging.getLogger("MyForceSubBot")

# Mengatur konfigurasi bot
API_ID = '15233392'
API_HASH = '9d5efc736450ff81e24fb074e74cf980'
BOT_TOKEN = '5719687586:AAE1l8DG27BkpJMwocT0GOYvT9NoF5m4lok'
CHANNEL = 'teastchahnel'
WELCOME_MSG = "Welcome {mention} to {title}!\n\nThanks for joining {channel}. There are {count} members now."
WELCOME_NOT_JOINED = "Hi {fullname}!\n\nPlease join @{channel} to access this chat."
ON_JOIN = True
ON_NEW_MSG = True

# Inisialisasi TelegramClient
client = TelegramClient('MyForceSubBot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Fungsi untuk memeriksa apakah pengguna sudah bergabung dengan saluran
async def is_user_joined(user_id):
    try:
        chat = await client.get_entity(CHANNEL)
        participants = await client.get_participants(chat)
        return any(participant.id == user_id for participant in participants)
    except ValueError as ve:
        log.error(f"Error checking if user is joined: {ve}")
        return False

# Event handler untuk tindakan bergabung pengguna ke grup
@client.on(events.ChatAction)
async def handle_user_join(event):
    if ON_JOIN and (event.user_joined or event.user_added):
        user = await event.get_user()
        chat = await event.get_chat()
        title = chat.title or "this chat"
        pp = await client.get_participants(chat)
        count = len(pp)
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        username = f"@{user.username}" if user.username else mention
        if await is_user_joined(user.id):
            msg = WELCOME_MSG.format(mention=mention, title=title, fullname=fullname, username=username, channel=CHANNEL, count=count)
            buttons = [
                [Button.inline("Sudah Join", data="join")],
                [Button.url("Channel", url=f"https://t.me/{CHANNEL}")]
            ]
        else:
            msg = WELCOME_NOT_JOINED.format(fullname=fullname, channel=CHANNEL)
            buttons = [
                [Button.inline("Sudah Join", data="join")],  # Add the "Sudah Join" button here
                [Button.url("Channel", url=f"https://t.me/{CHANNEL}")]
            ]
            await client.edit_permissions(chat, user, send_messages=False)  # Mute the user who hasn't joined the channel

        await event.reply(msg, buttons=buttons)

# Event handler untuk menangani tombol "Sudah Join"
@client.on(events.CallbackQuery(pattern=b"join"))
async def handle_join_callback(event):
    user_id = event.sender_id
    chat = await event.get_chat()
    if await is_user_joined(user_id):
        await event.answer("You've been unmuted!")
        await client.edit_permissions(chat, user_id, send_messages=True)  # Unmute the user
    else:
        await event.answer("You need to join the channel first.")

# Event handler untuk pesan baru yang masuk
@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    if not event.is_private and event.chat.id == CHANNEL:  # Pastikan pesan bukan dari obrolan pribadi dan dari grup yang benar
        # Cek apakah pengirim pesan belum bergabung dengan saluran
        if not (await is_user_joined(event.sender_id)):
            # Jika belum bergabung, kirim pesan balasan
            user = await event.get_sender()
            fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
            msg = f"Hi {fullname}!\n\nPlease join @{CHANNEL} to access this chat."
            buttons = [Button.inline("Sudah Join", data="join"), Button.url("Channel", url=f"https://t.me/{CHANNEL}")]
            await event.reply(msg, buttons=buttons)

# Fungsi untuk memeriksa apakah pesan adalah script Python
def is_python_script(text):
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False

# Jalankan program sampai terputus
client.run_until_disconnected()
