from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import os

# ================= CONFIG =================
api_id = 32052427
api_hash = "d9e14b1e99ac33e20d41479a47d2622f"
bot_token = "8094743137:AAFkASXCn4x7apzLgBfRn-r06m7hoHPvgzI"

FORCE_CHANNELS = [
    "chanaly_boot",
    "team_988"
]

OWNER = "Deva_harki"
AI_MODE = True
PANEL = True
# =========================================

app = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# ========= tools ==========
async def is_joined(client, user_id):
    for ch in FORCE_CHANNELS:
        try:
            await client.get_chat_member(ch, user_id)
        except UserNotParticipant:
            return False
        except:
            return False
    return True

def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Join @chanaly_boot", url="https://t.me/chanaly_boot")],
        [InlineKeyboardButton("✅ Join @team_988", url="https://t.me/team_988")]
    ])

# ========= start ==========
@app.on_message(filters.command("start"))
async def start(_, m):
    if not await is_joined(app, m.from_user.id):
        await m.reply(
            "⚠️ تکایە سەرەتا جۆینی جەناڵەکان بکە\n🤖 بوت زیرەکە",
            reply_markup=join_buttons()
        )
        return

    await m.reply(
        f"👋 بەخێربێیت {m.from_user.first_name}\n"
        f"🤖 AI MODE: {'ON' if AI_MODE else 'OFF'}\n"
        f"🎛 PANEL: {'ON' if PANEL else 'OFF'}\n\n"
        f"📌 دروستکراوە لەلاین @{OWNER}"
    )

# ========= message guard ==========
@app.on_message(filters.group & ~filters.service)
async def guard(_, m):
    if not m.from_user:
        return  # anonymous admin safe

    if not await is_joined(app, m.from_user.id):
        try:
            await m.delete()
        except:
            pass

        await m.reply(
            "⚠️ نامەکەت سڕایەوە\n"
            "👇 تکایە هەر ئێستا جۆینی جەناڵی گرووپ بکە",
            reply_markup=join_buttons()
        )

# ========= admin command ==========
@app.on_message(filters.command("deva") & filters.group)
async def deva(_, m):
    member = await app.get_chat_member(m.chat.id, m.from_user.id)

    if member.status not in ["administrator", "creator"]:
        await m.reply("❌ تۆ admin نیت")
        return

    await m.reply("✅ فەرمان وەرگیرا\n🤖 بوت ئامادەیە")

# ========= panel ==========
@app.on_message(filters.command("panel") & filters.private)
async def panel(_, m):
    global PANEL
    PANEL = not PANEL
    await m.reply(f"🎛 PANEL = {'ON' if PANEL else 'OFF'}")

# ========= AI ==========
@app.on_message(filters.command("ai") & filters.private)
async def ai(_, m):
    global AI_MODE
    AI_MODE = not AI_MODE
    await m.reply(f"🤖 AI MODE = {'ON' if AI_MODE else 'OFF'}")

print("BOT STARTED ...")
app.run()