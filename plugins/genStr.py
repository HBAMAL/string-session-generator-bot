import os
import json
import time
import asyncio

from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)


API_TEXT = """👋🏻 Hi {},

I am @Telsa_string_session_V2_bot.

MADE BY @TELSABOTS 

HIT /about To know More About Me

1st  send me your `API_ID` 😇
"""
HASH_TEXT = "Ok , Now Send your `API_HASH` 😇"
PHONE_NUMBER_TEXT = (
    "☎️__ Now send your Phone number with country code")



@Client.on_message(filters.private & filters.command("start"))
async def generate_str(c, m):
    get_api_id = await c.ask(
        chat_id=m.chat.id,
        text=API_TEXT.format(m.from_user.mention(style='md')),
        filters=filters.text
    )
    api_id = get_api_id.text
    if await is_cancel(m, api_id):
        return

    await get_api_id.delete()
    await get_api_id.request.delete()
    try:
        check_api = int(api_id)
    except Exception:
        await m.reply("**--😤 API ID Invalid 😤--**\nPress /start to Start Again, Once More .")
        return

    get_api_hash = await c.ask(
        chat_id=m.chat.id, 
        text=HASH_TEXT,
        filters=filters.text
    )
    api_hash = get_api_hash.text
    if await is_cancel(m, api_hash):
        return

    await get_api_hash.delete()
    await get_api_hash.request.delete()

    if not len(api_hash) >= 30:
        await m.reply("--**😤 API HASH Invalid 😤**--\nPress /start to Start Again, Once more.")
        return

    try:
        client = Client(":memory:", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await c.send_message(m.chat.id ,f"**🥴 ERROR: 🥴** `{str(e)}`\nPress /start to Start Again ,Once more .")
        return

    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    while True:
        get_phone_number = await c.ask(
            chat_id=m.chat.id,
            text=PHONE_NUMBER_TEXT
        )
        phone_number = get_phone_number.text
        if await is_cancel(m, phone_number):
            return
        await get_phone_number.delete()
        await get_phone_number.request.delete()

        confirm = await c.ask(
            chat_id=m.chat.id,
            text=f'🙄 Is `{phone_number}` correct? (y/n): \n\ntype: `y` (If Yes)\ntype: `n` (If No)'
        )
        if await is_cancel(m, confirm.text):
            return
        if "y" in confirm.text.lower():
            await confirm.delete()
            await confirm.request.delete()
            break
    try:
        code = await client.send_code(phone_number)
        await asyncio.sleep(1)
    except FloodWait as e:
        await m.reply(f"__🥺Sorry I Am Not Only For u , Plz wait For {e.x} Seconds ⏰__")
        return
    except ApiIdInvalid:
        await m.reply("😡 The API ID or API HASH is Invalid😡.\n\nPress /start to Start Again ,Once more")
        return
    except PhoneNumberInvalid:
        await m.reply("📞 Your Phone Number you provided is Not Crct❌.`\n\nPress /start to Start Again ,Once more")
        return

    try:
        sent_type = {"app": "🤩Telegram App 🤩",
            "sms": "💬SMS 💬",
            "call": "📱Phone call 📞",
            "flash_call": "📲Phone flash call 📞"
        }[code.type]
        otp = await c.ask(
            chat_id=m.chat.id,
            text=(f"Check I had sent an OTP to the number `{phone_number}` through {sent_type}\n\n"
                  "Please enter the OTP in the format `1 2 3 4 5` __(provied white space between numbers)__\n\n"
                  "Press /cancel to Cancel."), timeout=300)
    except TimeoutError:
        await m.reply("**⏳ TimeOut :** I can Only wait for 5 min.\nPress /start to  Start Again ,Once more")
        return
    if await is_cancel(m, otp.text):
        return
    otp_code = otp.text
    await otp.delete()
    await otp.request.delete()
    try:
        await client.sign_in(phone_number, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await m.reply("**🥵 Invalid Code**\n\nPress /start to Start Again ,Once more.")
        return 
    except PhoneCodeExpired:
        await m.reply("**☹️ Code  Expired**\n\nPress /start to Start Again ,Once more.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await c.ask(
                chat_id=m.chat.id, 
                text="` 🤭This account have two-step verification code.\nPlease enter your second factor authentication code.`\nPress /cancel to Cancel.",
                timeout=300
            )
        except TimeoutError:
            await m.reply("**⏳ TimeOut :** I can Only wait for 5 min.\nPress /start to Start Again ,Once mor.")
            return
        if await is_cancel(m, two_step_code.text):
            return
        new_code = two_step_code.text
        await two_step_code.delete()
        await two_step_code.request.delete()
        try:
            await client.check_password(new_code)
        except Exception as e:
            await m.reply(f"**⚠️ ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await c.send_message(m.chat.id ,f"**⚠️ ERROR⚠️:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"**Your String Session 👇**\n\n`{session_string}`\n\nThanks For using {(await c.get_me()).mention(style='md')}")
        text = "✅ Done Generated Your String Session and sent to you saved messages.\nCheck your saved messages ."
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="💚Channel💚", url=f"https://t.me/telsabots")]]
        )
        await c.send_message(m.chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await c.send_message(m.chat.id ,f"**⚠️ ERROR:** `{str(e)}`")
        return
    try:
        await client.stop()
    except:
        pass


@Client.on_message(filters.private & filters.command("help"))
async def help(c, m):
    await help_cb(c, m, cb=False)


@Client.on_callback_query(filters.regex('^help$'))
async def help_cb(c, m, cb=True):
    help_text = """**🆘Help🆘**


>>>> Press the start button

>>>> Send Your API_ID when bot ask.

>>>> Then send your API_HASH when bot ask.

>>>> Send your mobile number.

>>>> Send the OTP reciveved to your numer in the format `1 2 3 4 5` (Give space b/w each digit)

>>>> (If you have two step verification send to bot if bot ask.)


**NOTE:**

If you made any mistake anywhere press /cancel and then press /start
"""

    buttons = [[
        InlineKeyboardButton('📕 About', callback_data='about'),
        InlineKeyboardButton('❌ Close', callback_data='close')
    ]]
    if cb:
        await m.answer()
        await m.message.edit(text=help_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
    else:
        await m.reply_text(text=help_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True, quote=True)


@Client.on_message(filters.private & filters.command("about"))
async def about(c, m):
    await about_cb(c, m, cb=False)


@Client.on_callback_query(filters.regex('^about$'))
async def about_cb(c, m, cb=True):
    me = await c.get_me()
    about_text = f"""**MY PERSONAL INFO:**

__🤖BOT🤖:__ {me.mention(style='md')}

__👨‍💻 DEV🧑🏼‍💻:__ [꧁༒☬𝓗𝓑☬༒꧂](https://t.me/ALLUADDICT)

__📢 CHANNEL📢:__ [😇TELSA BOTS😇](https://t.me/telsabots)

__🎬MOVIES GROUP👥:__ [❤️HB GROUP❤️](https://t.me/FILIMSMOVIE)

__🤩SHARE🤩:__ [👉CLICK HERE👈](https://t.me/share/url?url=https://t.me/telsabots)

"""

    buttons = [[
        InlineKeyboardButton('🆘Help🆘', callback_data='help'),
        InlineKeyboardButton('🔐 Close🔐', callback_data='close')
    ]]
    if cb:
        await m.answer()
        await m.message.edit(about_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
    else:
        await m.reply_text(about_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True, quote=True)


@Client.on_callback_query(filters.regex('^close$'))
async def close(c, m):
    await m.message.delete()
    await m.message.reply_to_message.delete()


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("⛔ Process Cancelled.")
        return True
    return False


