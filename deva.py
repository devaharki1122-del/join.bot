import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ───────── CONFIG ─────────
api_id = 32052427
api_hash = "d9e14b1e99ac33e20d41479a47d2622f"
bot_token = "8094743137:AAFkASXCn4x7apzLgBfRn-r06m7hoHPvgzI"

BOT_USERNAME = "@Join_deva_bot"

FORCE_CHANNELS = [
    "@chanaly_boot",
    "@team_988"
]

CREDIT = (
    "\n\n━━━━━━━━━━━━━━\n"
    "🤖 بوت دروست کراوە لەلاین\n"
    "@Deva_harki\n"
    "━━━━━━━━━━━━━━"
)

app = Client("bot", api_id, api_hash, bot_token=bot_token)

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
db.commit()

# ───────── /start (PRIVATE) ─────────
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    not_joined = []

    for ch in FORCE_CHANNELS:
        try:
            m = await client.get_chat_member(ch, user.id)
            if m.status not in ["member", "administrator", "owner"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)

    if not_joined:
        buttons = [
            [InlineKeyboardButton(f"✅ Join {c}", url=f"https://t.me/{c.replace('@','')}")]
            for c in not_joined
        ]
        return await message.reply(
            "🔒 **Force Join Required**\n\n"
            "⚠️ بۆ بەکاربردنی بوت\n"
            "تکایە سەرەتا جەنالەکان جۆین بکە 👇"
            + CREDIT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    await message.reply(
        f"👋 سڵاو {user.first_name} 💙\n\n"
        "🤖 من بوتێکم کە دەتوانم ئەندامانی گرووپەکەت\n"
        "بنێرمە جەنالەکانت 🚀\n\n"
        "✨ ڕێنمایی:\n"
        "1️⃣ من زیاد بکە بۆ گرووپ\n"
        "2️⃣ من بکە admin 🛡️\n"
        "3️⃣ لە گرووپ بنوسە /deva\n\n"
        "👇 دەستپێبکە"
        + CREDIT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "➕ زیادم بکە بۆ گرووپ",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )]
        ])
    )

# ───────── /deva PANEL ─────────
@app.on_message(filters.group & filters.command("deva"))
async def deva(client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "owner"]:
        return await message.reply("❌ تۆ admin نیت")

    cur.execute("INSERT OR IGNORE INTO groups VALUES (?,?,?,?,?,?)",
                (message.chat.id, None, None, None, None, None))
    db.commit()

    await message.reply(
        "⚙️ پانێڵی بوت\n\n👇 هەڵبژێرە",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🖼️ دانانی وێنە", callback_data="photo")],
            [InlineKeyboardButton("🔗 دانانی جەنال 1", callback_data="ch1")],
            [InlineKeyboardButton("🔗 دانانی جەنال 2", callback_data="ch2")],
            [InlineKeyboardButton("🔗 دانانی جەنال 3", callback_data="ch3")]
        ])
    )

# ───────── CALLBACKS ─────────
@app.on_callback_query()
async def cb(client, query):
    chat_id = query.message.chat.id
    member = await client.get_chat_member(chat_id, query.from_user.id)
    if member.status not in ["administrator", "owner"]:
        return await query.answer("❌ admin نیت", show_alert=True)

    cur.execute("UPDATE groups SET waiting=? WHERE group_id=?",
                (query.data, chat_id))
    db.commit()

    if query.data == "photo":
        await query.message.reply("🖼️ تکایە وێنە بنێرە")
    else:
        await query.message.reply("🔗 تکایە @channel بنێرە")

    await query.answer("🤖 چاوەڕوانم")

# ───────── SAVE DATA ─────────
@app.on_message(filters.group)
async def save(client, message):
    cur.execute("SELECT waiting FROM groups WHERE group_id=?", (message.chat.id,))
    row = cur.fetchone()
    if not row or not row[0]:
        return

    w = row[0]

    if w == "photo" and message.photo:
        cur.execute("UPDATE groups SET photo=?, waiting=NULL WHERE group_id=?",
                    (message.photo[-1].file_id, message.chat.id))
        db.commit()
        return await message.reply("✅ وێنە هەڵگیرا")

    if w in ["ch1","ch2","ch3"] and message.text and message.text.startswith("@"):
        cur.execute(f"UPDATE groups SET {w}=?, waiting=NULL WHERE group_id=?",
                    (message.text, message.chat.id))
        db.commit()
        return await message.reply("✅ جەنال هەڵگیرا")

app.run()