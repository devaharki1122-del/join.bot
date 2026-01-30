import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus

# ───────── CONFIG ─────────
api_id = 32052427
api_hash = "d9e14b1e99ac33e20d41479a47d2622f"
bot_token = "8094743137:AAFwDQq6hdXm-RZWLN8eJDFxJ5r8gCYXEX0"

BOT_USERNAME = "Join_deva_bot"

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

# ───────── APP ─────────
app = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

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
    waiting TEXT,
    panel INTEGER DEFAULT 1
)
""")
db.commit()

# ───────── FORCE JOIN CHECK ─────────
async def check_force_join(client, user_id):
    for ch in FORCE_CHANNELS:
        try:
            m = await client.get_chat_member(ch, user_id)
            if m.status not in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]:
                return False
        except:
            return False
    return True

# ───────── START ─────────
@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user

    ok = await check_force_join(client, user.id)
    if not ok:
        buttons = [
            [InlineKeyboardButton(
                f"✅ Join {ch}",
                url=f"https://t.me/{ch.replace('@','')}"
            )]
            for ch in FORCE_CHANNELS
        ]
        return await message.reply(
            "🔒 **Force Join Required**\n\n"
            "⚠️ تکایە سەرەتا جەنالەکان جۆین بکە 👇"
            + CREDIT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    await message.reply(
        f"👋 سڵاو {user.first_name}\n"
        "🤖 من بوتێکی زێرەکم (AI)\n\n"
        "➕ من زیاد بکە بۆ گرووپ و adminم بکە\n"
        "📌 پاشان لە گرووپ بنوسە /deva"
        + CREDIT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "➕ زیادم بکە بۆ گرووپ",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )]
        ])
    )

# ───────── GROUP FORCE JOIN (AI SMART) ─────────
@app.on_message(filters.group & ~filters.service)
async def force_join_group(client, message):
    if not message.from_user:
        return

    ok = await check_force_join(client, message.from_user.id)
    if ok:
        return

    try:
        await message.delete()
    except:
        pass

    buttons = [
        [InlineKeyboardButton(
            f"✅ Join {ch}",
            url=f"https://t.me/{ch.replace('@','')}"
        )]
        for ch in FORCE_CHANNELS
    ]

    await message.reply(
        "⚠️ **ئەندام نیت**\n\n"
        "تکایە هەردوو جەنال جۆین بکە 👇\n"
        "دوای ئەوە دەتوانیت نامە بنێریت"
        + CREDIT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ───────── /deva PANEL ─────────
@app.on_message(filters.group & filters.command("deva"))
async def deva(client, message):

    # ✅ anonymous admin fix
    if message.sender_chat:
        member = await client.get_chat_member(message.chat.id, message.sender_chat.id)
    else:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)

    if member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    ]:
        return await message.reply("❌ تۆ admin نیت")

    cur.execute("INSERT OR IGNORE INTO groups(group_id) VALUES (?)", (message.chat.id,))
    db.commit()

    await message.reply(
        "⚙️ **پانێڵی زێرەکی بوت**\n\n👇 هەڵبژێرە",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🖼️ دانانی وێنە", callback_data="photo")],
            [InlineKeyboardButton("🔗 دانانی جەنال 1", callback_data="ch1")],
            [InlineKeyboardButton("🔗 دانانی جەنال 2", callback_data="ch2")],
            [InlineKeyboardButton("🔗 دانانی جەنال 3", callback_data="ch3")],
            [InlineKeyboardButton("🎛 panel on/off", callback_data="panel")]
        ])
    )

# ───────── CALLBACK ─────────
@app.on_callback_query()
async def callbacks(client, query):
    chat_id = query.message.chat.id

    # admin check (fix)
    if query.message.sender_chat:
        member = await client.get_chat_member(chat_id, query.message.sender_chat.id)
    else:
        member = await client.get_chat_member(chat_id, query.from_user.id)

    if member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    ]:
        return await query.answer("❌ admin نیت", show_alert=True)

    if query.data == "panel":
        cur.execute("SELECT panel FROM groups WHERE group_id=?", (chat_id,))
        st = cur.fetchone()[0]
        new = 0 if st else 1
        cur.execute("UPDATE groups SET panel=? WHERE group_id=?", (new, chat_id))
        db.commit()
        return await query.answer("✅ panel گۆڕا")

    cur.execute("UPDATE groups SET waiting=? WHERE group_id=?",
                (query.data, chat_id))
    db.commit()

    await query.message.reply(
        "📥 تکایە بنێرە",
    )
    await query.answer("🤖 AI چاوەڕوانە")

# ───────── SAVE DATA ─────────
@app.on_message(filters.group)
async def save_data(client, message):
    cur.execute("SELECT waiting FROM groups WHERE group_id=?", (message.chat.id,))
    row = cur.fetchone()
    if not row or not row[0]:
        return

    w = row[0]

    if w == "photo" and message.photo:
        cur.execute(
            "UPDATE groups SET photo=?, waiting=NULL WHERE group_id=?",
            (message.photo[-1].file_id, message.chat.id)
        )
        db.commit()
        return await message.reply("✅ وێنە هەڵگیرا")

    if w in ["ch1", "ch2", "ch3"] and message.text:
        cur.execute(
            f"UPDATE groups SET {w}=?, waiting=NULL WHERE group_id=?",
            (message.text, message.chat.id)
        )
        db.commit()
        return await message.reply("✅ جەنال هەڵگیرا")

# ───────── RUN ─────────
app.run()