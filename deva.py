import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired

# ============ CONFIG ============
api_id = 32052427
api_hash = "d9e14b1e99ac33e20d41479a47d2622f"
bot_token = "8094743137:AAHO66lQbJXT22RhpDZMgyK5Jz26vHuGzCE"

BOT_USERNAME = "Join_deva_bot"

FORCE_CHANNELS = ["@chanaly_boot", "@team_988"]

CREDIT = "\n\n━━━━━━━━━━━━━━\n🤖 بوت دروست کراوە لەلاین\n@Deva_harki\n━━━━━━━━━━━━━━"
# =================================

app = Client("bot", api_id, api_hash, bot_token=bot_token)

# ============ DB ============
db = sqlite3.connect("data.db", check_same_thread=False)
cur = db.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS groups(
    group_id INTEGER PRIMARY KEY,
    photo TEXT,
    ch1 TEXT,
    ch2 TEXT,
    ch3 TEXT,
    waiting TEXT
)
""")
db.commit()

# ============ FORCE JOIN ============
async def force_join_ok(client, user_id):
    for ch in FORCE_CHANNELS:
        try:
            m = await client.get_chat_member(ch, user_id)
            if m.status not in ("member", "administrator", "creator"):
                return False
        except UserNotParticipant:
            return False
        except:
            return True  # اگر بوت admin نەبوو → skip
    return True

# ============ START ============
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    if not await force_join_ok(client, message.from_user.id):
        btn = [
            [InlineKeyboardButton(f"✅ Join {c}", url=f"https://t.me/{c.replace('@','')}")]
            for c in FORCE_CHANNELS
        ]
        return await message.reply(
            "🔒 بۆ بەکاربردنی بوت، سەرەتا جۆین بکە 👇" + CREDIT,
            reply_markup=InlineKeyboardMarkup(btn)
        )

    await message.reply(
        f"👋 سڵاو {message.from_user.first_name} 💙\n\n"
        "🤖 من دەتوانم ئەندامانی گرووپەکەت بنێرمە جەنالەکانت 🚀\n\n"
        "1️⃣ زیادم بکە بۆ گرووپ\n"
        "2️⃣ بکەم admin\n"
        "3️⃣ لە گرووپ بنوسە /deva\n"
        + CREDIT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ زیادم بکە بۆ گرووپ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]
        ])
    )

# ============ PANEL ============
@app.on_message(filters.group & filters.command("deva"))
async def panel(client, message):
    try:
        m = await client.get_chat_member(message.chat.id, message.from_user.id)
        if m.status not in ("administrator", "creator"):
            return await message.reply("❌ تۆ admin نیت")
    except:
        return await message.reply("❌ ناتوانم admin پشکنین بکەم")

    cur.execute("INSERT OR IGNORE INTO groups VALUES (?,?,?,?,?,?)",
                (message.chat.id, None, None, None, None, None))
    db.commit()

    await message.reply(
        "⚙️ پانێڵ",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🖼️ دانانی وێنە", callback_data="photo")],
            [InlineKeyboardButton("🔗 جەنال 1", callback_data="ch1")],
            [InlineKeyboardButton("🔗 جەنال 2", callback_data="ch2")],
            [InlineKeyboardButton("🔗 جەنال 3", callback_data="ch3")]
        ])
    )

# ============ CALLBACK ============
@app.on_callback_query()
async def cb(client, q):
    try:
        m = await client.get_chat_member(q.message.chat.id, q.from_user.id)
        if m.status not in ("administrator", "creator"):
            return await q.answer("❌ admin نیت", show_alert=True)
    except:
        return await q.answer("❌ ناتوانم admin پشکنین بکەم", show_alert=True)

    cur.execute("UPDATE groups SET waiting=? WHERE group_id=?",
                (q.data, q.message.chat.id))
    db.commit()

    await q.message.reply("📩 نێرە")
    await q.answer()

# ============ SAVE ============
@app.on_message(filters.group)
async def save(client, message):
    cur.execute("SELECT waiting FROM groups WHERE group_id=?", (message.chat.id,))
    r = cur.fetchone()
    if not r or not r[0]:
        return

    w = r[0]
    if w == "photo" and message.photo:
        cur.execute("UPDATE groups SET photo=?, waiting=NULL WHERE group_id=?",
                    (message.photo[-1].file_id, message.chat.id))
        db.commit()
        return await message.reply("✅ وێنە هەڵگیرا")

    if w in ("ch1","ch2","ch3") and message.text and message.text.startswith("@"):
        cur.execute(f"UPDATE groups SET {w}=?, waiting=NULL WHERE group_id=?",
                    (message.text, message.chat.id))
        db.commit()
        return await message.reply("✅ جەنال هەڵگیرا")

app.run()