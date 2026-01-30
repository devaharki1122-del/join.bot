import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ───────── CONFIG ─────────
api_id = 32052427
api_hash = "d9e14b1e99ac33e20d41479a47d2622f"
bot_token = "8094743137:AAEQwaFQPym1x1wZsZ6qHOHwiIubovPvbX8"

BOT_USERNAME = "Join_deva_bot"

FORCE_CHANNELS = ["@chanaly_boot", "@team_988"]

CREDIT = (
    "\n\n━━━━━━━━━━━━━━\n"
    "🤖 بوت دروست کراوە لەلاین\n"
    "@Deva_harki\n"
    "━━━━━━━━━━━━━━"
)

app = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# ───────── DB ─────────
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

cur.execute("""
CREATE TABLE IF NOT EXISTS settings(
    group_id INTEGER PRIMARY KEY,
    force_join INTEGER DEFAULT 1,
    smart INTEGER DEFAULT 1
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS warned(
    user_id INTEGER,
    group_id INTEGER,
    PRIMARY KEY(user_id, group_id)
)
""")
db.commit()

# ───────── FORCE JOIN CHECK ─────────
async def check_force_join(client, user_id):
    for ch in FORCE_CHANNELS:
        try:
            m = await client.get_chat_member(ch, user_id)
            if m.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ───────── /start PRIVATE ─────────
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user

    if not await check_force_join(client, user.id):
        buttons = [[InlineKeyboardButton(f"✅ Join {c}", url=f"https://t.me/{c.replace('@','')}")] for c in FORCE_CHANNELS]
        return await message.reply(
            "🔒 بۆ بەکاربردنی بوت\n"
            "تکایە سەرەتا جەنالەکان جۆین بکە 👇" + CREDIT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    await message.reply(
        f"👋 سڵاو {user.first_name} 💙\n\n"
        "من دەتوانم ئەندامانی گرووپەکەت بنێرمە جەنالەکانت 🚀\n\n"
        "1️⃣ من زیاد بکە بۆ گرووپ\n"
        "2️⃣ من بکە admin\n"
        "3️⃣ لە گرووپ /deva بنوسە\n" + CREDIT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ زیادم بکە بۆ گرووپ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]
        ])
    )

# ───────── /deva PANEL ─────────
@app.on_message(filters.group & filters.command("deva"))
async def deva(client, message):
    m = await client.get_chat_member(message.chat.id, message.from_user.id)
    if m.status not in ["administrator", "creator"]:
        return await message.reply("❌ تۆ admin نیت")

    cur.execute("INSERT OR IGNORE INTO groups VALUES (?,?,?,?,?,?)",
                (message.chat.id, None, None, None, None, None))
    cur.execute("INSERT OR IGNORE INTO settings VALUES (?,?,?)",
                (message.chat.id, 1, 1))
    db.commit()

    await message.reply(
        "🎛 پانێڵی بەڕێوەبردن",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🖼️ دانانی وێنە", callback_data="photo")],
            [InlineKeyboardButton("🔗 دانانی جەنال 1", callback_data="ch1")],
            [InlineKeyboardButton("🔗 دانانی جەنال 2", callback_data="ch2")],
            [InlineKeyboardButton("🔗 دانانی جەنال 3", callback_data="ch3")],
            [InlineKeyboardButton("🎛 Force Join ON/OFF", callback_data="toggle_force")],
            [InlineKeyboardButton("🤖 AI Smart ON/OFF", callback_data="toggle_smart")]
        ])
    )

# ───────── CALLBACKS ─────────
@app.on_callback_query()
async def cb(client, q):
    chat_id = q.message.chat.id
    m = await client.get_chat_member(chat_id, q.from_user.id)
    if m.status not in ["administrator", "creator"]:
        return await q.answer("❌ admin نیت", show_alert=True)

    if q.data in ["photo","ch1","ch2","ch3"]:
        cur.execute("UPDATE groups SET waiting=? WHERE group_id=?", (q.data, chat_id))
        db.commit()
        await q.message.reply("📥 تکایە ناردن بکە")
        return await q.answer()

    if q.data == "toggle_force":
        cur.execute("UPDATE settings SET force_join = 1 - force_join WHERE group_id=?", (chat_id,))
        db.commit()
        return await q.answer("🎛 گۆڕا")

    if q.data == "toggle_smart":
        cur.execute("UPDATE settings SET smart = 1 - smart WHERE group_id=?", (chat_id,))
        db.commit()
        return await q.answer("🤖 گۆڕا")

# ───────── SAVE DATA ─────────
@app.on_message(filters.group)
async def save_data(client, message):
    cur.execute("SELECT waiting FROM groups WHERE group_id=?", (message.chat.id,))
    row = cur.fetchone()
    if not row or not row[0]:
        return

    w = row[0]
    if w == "photo" and message.photo:
        cur.execute("UPDATE groups SET photo=?, waiting=NULL WHERE group_id=?",
                    (message.photo[-1].file_id, message.chat.id))
    elif w in ["ch1","ch2","ch3"] and message.text and message.text.startswith("@"):
        cur.execute(f"UPDATE groups SET {w}=?, waiting=NULL WHERE group_id=?",
                    (message.text, message.chat.id))
    db.commit()
    await message.reply("✅ هەڵگیرا")

# ───────── FORCE JOIN GROUP (FINAL) ─────────
@app.on_message(filters.group & ~filters.service)
async def force_join_group(client, message):
    if message.from_user is None:
        return

    cur.execute("SELECT force_join, smart FROM settings WHERE group_id=?", (message.chat.id,))
    row = cur.fetchone()
    if not row or row[0] == 0:
        return

    if await check_force_join(client, message.from_user.id):
        return

    try:
        await message.delete()
    except:
        pass

    if row[1] == 1:
        cur.execute("SELECT 1 FROM warned WHERE user_id=? AND group_id=?",
                    (message.from_user.id, message.chat.id))
        if cur.fetchone():
            return
        cur.execute("INSERT OR IGNORE INTO warned VALUES (?,?)",
                    (message.from_user.id, message.chat.id))
        db.commit()

    cur.execute("SELECT ch1, ch2, ch3 FROM groups WHERE group_id=?", (message.chat.id,))
    chs = cur.fetchone()

    buttons = []
    if chs:
        for ch in chs:
            if ch:
                buttons.append([InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch.replace('@','')}")])

    await message.reply(
        "🚫 نامەکەت سڕایەوە\n\n"
        "🔐 تکایە هەر ئێستا جۆینی جەنالەکان بکە 👇\n"
        "⚡ دوای جۆین → نامە بنێرە"
        + CREDIT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ───────── RUN ─────────
app.run()