"""
GeniusKexBot — Production Telegram Bot
30 Utility Tools + NVIDIA AI (/ask command)
Render Worker Deployment Ready
"""

import logging
import sqlite3
from db_wrapper import init_db, execute_query
import datetime
import random
import string
import re
import requests
from bs4 import BeautifulSoup
import asyncio
import os
import json
import hashlib
import base64
import socket

try:
    import whois as python_whois
except ImportError:
    python_whois = None

from openai import OpenAI

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# ============ CONFIG (ENV VARS) ============
TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
DATABASE_URL = os.environ.get("DATABASE_URL", "geniuskex.db")
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# ============ LOGGING ============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ STATES ============
URL_SHORTENER_STATE = 1
QR_CODE_GENERATOR_STATE = 2
DOWNLOADER_STATE = 3
CALCULATOR_STATE = 4
UNIT_CONVERTER_STATE = 5
WEATHER_CHECK_STATE = 6
PASSWORD_GENERATOR_STATE = 7
NOTES_STATE = 8
WEBSITE_TRAFFIC_STATE = 9
IP_LOOKUP_STATE = 10
PHONE_LOOKUP_STATE = 11
EMAIL_CHECK_STATE = 12
WHOIS_LOOKUP_STATE = 13
PORT_SCANNER_STATE = 14
HEADER_ANALYZER_STATE = 15
HASH_GENERATOR_STATE = 16
BASE64_STATE = 17
DNS_LOOKUP_STATE = 18
SUBDOMAIN_FINDER_STATE = 19
LINK_ANALYZER_STATE = 20
BROADCAST_STATE = 21
AI_ASK_STATE = 22
AI_IMAGE_STATE = 23
AI_CODE_STATE = 24
AI_TRANSLATE_STATE = 25
AI_SUMMARIZE_STATE = 26
AI_REWRITE_STATE = 27
AI_EXPLAIN_STATE = 28
AI_ROAST_STATE = 29
AI_BUSINESS_STATE = 30
AI_SEO_STATE = 31
AI_CAPTION_STATE = 32
TEMP_MAIL_STATE = 33
CRYPTO_PRICE_STATE = 34
TIMEZONE_STATE = 35
COLOR_PALETTE_STATE = 36

# ============ DATABASE ============
def register_user(telegram_id, username, first_name, last_name, referred_by=None):
    try:
        referral_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        execute_query(
            "INSERT INTO users (telegram_id, username, first_name, last_name, referral_code, referred_by) VALUES (?, ?, ?, ?, ?, ?)",
            (telegram_id, username, first_name, last_name, referral_code, referred_by),
            commit=True
        )
        if referred_by:
            execute_query("UPDATE users SET referral_points = referral_points + 1 WHERE telegram_id = ?", (referred_by,), commit=True)
        return True
    except Exception:
        return False

def get_user(telegram_id):
    return execute_query("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,), fetchone=True)

def update_daily_bonus_claimed_at(telegram_id):
    now = datetime.datetime.now().isoformat()
    execute_query("UPDATE users SET daily_bonus_claimed_at = ? WHERE telegram_id = ?", (now, telegram_id), commit=True)

def get_all_users():
    users = execute_query("SELECT telegram_id FROM users", fetchall=True)
    return [row["telegram_id"] for row in users] if users else []

def add_note(user_id, note_text):
    execute_query("INSERT INTO notes (user_id, note_text) VALUES (?, ?)", (user_id, note_text), commit=True)

def get_notes(user_id):
    notes = execute_query("SELECT note_text FROM notes WHERE user_id = ?", (user_id,), fetchall=True)
    return [row["note_text"] for row in notes] if notes else []

def get_secret_vault_content(referral_unlock_count):
    return execute_query("SELECT title, content FROM secret_vault WHERE referral_unlock_count <= ?", (referral_unlock_count,), fetchall=True)

# ============ NVIDIA AI ============
def nvidia_ai_chat(prompt: str) -> str:
    if not NVIDIA_API_KEY:
        return "⚠️ NVIDIA API key not configured. Set NVIDIA_API_KEY env variable."
    try:
        client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)
        completion = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": "You are Genius Kex AI, a powerful and helpful assistant. Be concise, accurate, and direct. Max 500 words."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"NVIDIA AI error: {e}")
        return f"⚠️ AI Error: {str(e)[:200]}"

# ============ MENUS ============
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔗 URL Shortener", callback_data="url_shortener"),
         InlineKeyboardButton("📸 QR Code", callback_data="qr_code_generator")],
        [InlineKeyboardButton("⬇️ YT/IG Download", callback_data="downloader"),
         InlineKeyboardButton("📈 Earnings", callback_data="earning_dashboard")],
        [InlineKeyboardButton("💰 Daily Bonus", callback_data="daily_bonus"),
         InlineKeyboardButton("🔢 Calculator", callback_data="calculator")],
        [InlineKeyboardButton("🔄 Unit Convert", callback_data="unit_converter"),
         InlineKeyboardButton("☁️ Weather", callback_data="weather_check")],
        [InlineKeyboardButton("🔐 Password Gen", callback_data="password_generator"),
         InlineKeyboardButton("📝 Notes", callback_data="notes")],
        [InlineKeyboardButton("🌐 Site Traffic", callback_data="website_traffic"),
         InlineKeyboardButton("💎 Secret Vault", callback_data="secret_vault")],
        [InlineKeyboardButton("🤖 Ask AI", callback_data="ai_ask"),
         InlineKeyboardButton("💀 DARK TOOLS 💀", callback_data="dark_tools_menu")],
        [InlineKeyboardButton("🧠 AI TOOLS 2026", callback_data="ai_tools_menu"),
         InlineKeyboardButton("⚡ POWER TOOLS", callback_data="power_tools_menu")],
        [InlineKeyboardButton("🤝 My Referral Link", callback_data="my_referral_link")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_ai_tools_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎨 AI Image Prompt", callback_data="ai_image"),
         InlineKeyboardButton("💻 AI Code Gen", callback_data="ai_code")],
        [InlineKeyboardButton("🌐 AI Translate", callback_data="ai_translate"),
         InlineKeyboardButton("📋 AI Summarize", callback_data="ai_summarize")],
        [InlineKeyboardButton("✍️ AI Rewrite", callback_data="ai_rewrite"),
         InlineKeyboardButton("🧠 AI Explain", callback_data="ai_explain")],
        [InlineKeyboardButton("🔥 AI Roast", callback_data="ai_roast"),
         InlineKeyboardButton("💼 AI Business", callback_data="ai_business")],
        [InlineKeyboardButton("📈 AI SEO", callback_data="ai_seo"),
         InlineKeyboardButton("📸 AI Caption", callback_data="ai_caption")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_power_tools_keyboard():
    keyboard = [
        [InlineKeyboardButton("📧 Temp Mail", callback_data="temp_mail"),
         InlineKeyboardButton("💰 Crypto Price", callback_data="crypto_price")],
        [InlineKeyboardButton("🕐 Timezone Convert", callback_data="timezone_convert"),
         InlineKeyboardButton("🎨 Color Palette", callback_data="color_palette")],
        [InlineKeyboardButton("📊 JSON Formatter", callback_data="json_formatter"),
         InlineKeyboardButton("🔗 Webhook Tester", callback_data="webhook_tester")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_dark_tools_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎯 IP Lookup", callback_data="ip_lookup"),
         InlineKeyboardButton("📱 Phone Lookup", callback_data="phone_lookup")],
        [InlineKeyboardButton("📧 Email Breach", callback_data="email_check"),
         InlineKeyboardButton("🕵️ WHOIS Lookup", callback_data="whois_lookup")],
        [InlineKeyboardButton("🔓 Port Scanner", callback_data="port_scanner"),
         InlineKeyboardButton("🛡️ Header Analyze", callback_data="header_analyzer")],
        [InlineKeyboardButton("🧬 Hash Gen", callback_data="hash_generator"),
         InlineKeyboardButton("🔀 Base64 En/De", callback_data="base64_tool")],
        [InlineKeyboardButton("🌍 DNS Lookup", callback_data="dns_lookup"),
         InlineKeyboardButton("👤 Fake ID Gen", callback_data="fake_identity")],
        [InlineKeyboardButton("🕸️ Subdomain Find", callback_data="subdomain_finder"),
         InlineKeyboardButton("🔍 Link Analyzer", callback_data="link_analyzer")],
        [InlineKeyboardButton("🧅 Dark Web Email", callback_data="darkweb_email")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============ COMMAND HANDLERS ============
async def start(update: Update, context) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name

    referred_by = None
    if context.args and len(context.args) > 0:
        ref_code = context.args[0]
        referrer = execute_query("SELECT telegram_id FROM users WHERE referral_code = ?", (ref_code,), fetchone=True)
        if referrer:
            referred_by = referrer["telegram_id"]

    if not get_user(user_id):
        register_user(user_id, username, first_name, last_name, referred_by)
        welcome_message = f"⚡ Welcome, {first_name}! You've entered Genius Kex Bot. "
        if referred_by:
            welcome_message += "Referred by a power user! "
    else:
        welcome_message = f"⚡ Welcome back, {first_name}! "

    welcome_message += "45+ elite tools + AI arsenal at your command. Choose wisely:"

    await update.message.reply_text(welcome_message, reply_markup=get_main_menu_keyboard())
    context.user_data["state"] = None

async def help_command(update: Update, context) -> None:
    help_text = (
        "🤖 Genius Kex Bot — Commands\n\n"
        "/start - Main menu\n"
        "/ask <question> - Ask AI anything\n"
        "/viewnotes - View saved notes\n"
        "/broadcast <msg> - Admin broadcast\n"
        "/help - This message"
    )
    await update.message.reply_text(help_text, reply_markup=get_main_menu_keyboard())

async def ask_command(update: Update, context) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /ask <your question>\nExample: /ask What is quantum computing?", reply_markup=get_main_menu_keyboard())
        return
    question = " ".join(context.args)
    await update.message.reply_text("🤖 Thinking...")
    answer = nvidia_ai_chat(question)
    await update.message.reply_text(f"🤖 AI Response:\n\n{answer}", reply_markup=get_main_menu_keyboard())

# ============ BUTTON HANDLER ============
async def button(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    feature = query.data
    user_id = query.from_user.id
    user = get_user(user_id)

    # Navigation
    if feature == "main_menu":
        await query.edit_message_text("⚡ Main Menu - Choose a feature:", reply_markup=get_main_menu_keyboard())
        context.user_data["state"] = None
        return
    elif feature == "dark_tools_menu":
        await query.edit_message_text("💀 DARK TOOLS - Choose your weapon:", reply_markup=get_dark_tools_keyboard())
        context.user_data["state"] = None
        return
    elif feature == "ai_tools_menu":
        await query.edit_message_text("🧠 AI TOOLS 2026 - Next-gen AI power:", reply_markup=get_ai_tools_keyboard())
        context.user_data["state"] = None
        return
    elif feature == "power_tools_menu":
        await query.edit_message_text("⚡ POWER TOOLS - Utility arsenal:", reply_markup=get_power_tools_keyboard())
        context.user_data["state"] = None
        return

    # AI Ask
    if feature == "ai_ask":
        context.user_data["state"] = AI_ASK_STATE
        await query.edit_message_text("🤖 Ask me anything! Send your question:")
        return

    # Original features
    if feature == "url_shortener":
        context.user_data["state"] = URL_SHORTENER_STATE
        await query.edit_message_text("🔗 Send me the URL to shorten:")
    elif feature == "qr_code_generator":
        context.user_data["state"] = QR_CODE_GENERATOR_STATE
        await query.edit_message_text("📸 Send me the URL or text for QR code:")
    elif feature == "downloader":
        context.user_data["state"] = DOWNLOADER_STATE
        await query.edit_message_text("⬇️ Send me the YouTube or Instagram video link:")
    elif feature == "earning_dashboard":
        if user:
            referral_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user['referral_code']}"
            await query.edit_message_text(
                f"📈 Earning Dashboard\n\n"
                f"💰 Points: {user['referral_points']}\n"
                f"🔗 Your Link: {referral_link}",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await query.edit_message_text("User not found. Use /start first.", reply_markup=get_main_menu_keyboard())
        context.user_data["state"] = None
    elif feature == "daily_bonus":
        if user:
            last_claimed_str = user["daily_bonus_claimed_at"]
            if last_claimed_str:
                last_claimed = datetime.datetime.fromisoformat(last_claimed_str)
                if (datetime.datetime.now() - last_claimed).total_seconds() < 86400:
                    await query.edit_message_text("⏰ Already claimed today! Come back tomorrow.", reply_markup=get_main_menu_keyboard())
                    context.user_data["state"] = None
                    return
            update_daily_bonus_claimed_at(user_id)
            execute_query("UPDATE users SET referral_points = referral_points + 5 WHERE telegram_id = ?", (user_id,), commit=True)
            await query.edit_message_text("🎉 +5 points claimed! Daily bonus collected.", reply_markup=get_main_menu_keyboard())
        else:
            await query.edit_message_text("User not found. Use /start first.", reply_markup=get_main_menu_keyboard())
        context.user_data["state"] = None
    elif feature == "calculator":
        context.user_data["state"] = CALCULATOR_STATE
        await query.edit_message_text("🔢 Send a math expression (e.g., 5 + 3 * 2):")
    elif feature == "unit_converter":
        context.user_data["state"] = UNIT_CONVERTER_STATE
        await query.edit_message_text("🔄 Send value and units (e.g., 10 km to miles):")
    elif feature == "weather_check":
        context.user_data["state"] = WEATHER_CHECK_STATE
        await query.edit_message_text("☁️ Send city name:")
    elif feature == "password_generator":
        context.user_data["state"] = PASSWORD_GENERATOR_STATE
        await query.edit_message_text("🔐 How many characters? (6-50):")
    elif feature == "notes":
        context.user_data["state"] = NOTES_STATE
        await query.edit_message_text("📝 Send your note to save.\nUse /viewnotes to view all.")
    elif feature == "website_traffic":
        context.user_data["state"] = WEBSITE_TRAFFIC_STATE
        await query.edit_message_text("🌐 Send website URL:")
    elif feature == "secret_vault":
        if user:
            if user["referral_points"] >= 5:
                secrets = get_secret_vault_content(user["referral_points"])
                if secrets:
                    secret_messages = [f"*{s['title']}*\n{s['content']}" for s in secrets]
                    await query.edit_message_text("💎 Secret Vault Unlocked!\n\n" + "\n\n".join(secret_messages), parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
                else:
                    await query.edit_message_text("No secrets yet.", reply_markup=get_main_menu_keyboard())
            else:
                await query.edit_message_text(f"🔒 Locked! Need 5 points. You have {user['referral_points']}.", reply_markup=get_main_menu_keyboard())
        else:
            await query.edit_message_text("User not found. Use /start first.", reply_markup=get_main_menu_keyboard())
        context.user_data["state"] = None
    elif feature == "my_referral_link":
        if user:
            referral_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user['referral_code']}"
            await query.edit_message_text(f"🤝 Your referral link:\n{referral_link}\n\nShare to earn points!", reply_markup=get_main_menu_keyboard())
        else:
            await query.edit_message_text("User not found. Use /start first.", reply_markup=get_main_menu_keyboard())
        context.user_data["state"] = None

    # ===== DARK TOOLS =====
    elif feature == "ip_lookup":
        context.user_data["state"] = IP_LOOKUP_STATE
        await query.edit_message_text("🎯 Send an IP address to trace:")
    elif feature == "phone_lookup":
        context.user_data["state"] = PHONE_LOOKUP_STATE
        await query.edit_message_text("📱 Send a phone number (with country code, e.g., +911234567890):")
    elif feature == "email_check":
        context.user_data["state"] = EMAIL_CHECK_STATE
        await query.edit_message_text("📧 Send an email to check for breaches:")
    elif feature == "whois_lookup":
        context.user_data["state"] = WHOIS_LOOKUP_STATE
        await query.edit_message_text("🕵️ Send a domain name (e.g., google.com):")
    elif feature == "port_scanner":
        context.user_data["state"] = PORT_SCANNER_STATE
        await query.edit_message_text("🔓 Send IP or domain to scan ports:")
    elif feature == "header_analyzer":
        context.user_data["state"] = HEADER_ANALYZER_STATE
        await query.edit_message_text("🛡️ Send a URL to analyze security headers:")
    elif feature == "hash_generator":
        context.user_data["state"] = HASH_GENERATOR_STATE
        await query.edit_message_text("🧬 Send text to generate hashes (MD5, SHA1, SHA256, SHA512):")
    elif feature == "base64_tool":
        context.user_data["state"] = BASE64_STATE
        await query.edit_message_text("🔀 Send text to encode/decode.\nPrefix with 'encode:' or 'decode:'\nExample: encode:hello world")
    elif feature == "dns_lookup":
        context.user_data["state"] = DNS_LOOKUP_STATE
        await query.edit_message_text("🌍 Send a domain to lookup DNS records:")
    elif feature == "fake_identity":
        await handle_fake_identity(query)
        context.user_data["state"] = None
    elif feature == "subdomain_finder":
        context.user_data["state"] = SUBDOMAIN_FINDER_STATE
        await query.edit_message_text("🕸️ Send a domain to find subdomains:")
    elif feature == "link_analyzer":
        context.user_data["state"] = LINK_ANALYZER_STATE
        await query.edit_message_text("🔍 Send a URL to analyze if it's safe:")
    elif feature == "darkweb_email":
        context.user_data["state"] = EMAIL_CHECK_STATE
        await query.edit_message_text("🧅 Send an email to check dark web exposure:")

    # ===== AI TOOLS 2026 =====
    elif feature == "ai_image":
        context.user_data["state"] = AI_IMAGE_STATE
        await query.edit_message_text("🎨 Describe the image you want AI to create a prompt for:")
    elif feature == "ai_code":
        context.user_data["state"] = AI_CODE_STATE
        await query.edit_message_text("💻 Describe what code you need (language + task):")
    elif feature == "ai_translate":
        context.user_data["state"] = AI_TRANSLATE_STATE
        await query.edit_message_text("🌐 Send text to translate.\nFormat: [target language] your text\nExample: Spanish Hello how are you")
    elif feature == "ai_summarize":
        context.user_data["state"] = AI_SUMMARIZE_STATE
        await query.edit_message_text("📋 Send long text to summarize (AI will condense it):")
    elif feature == "ai_rewrite":
        context.user_data["state"] = AI_REWRITE_STATE
        await query.edit_message_text("✍️ Send text to rewrite in a better way:")
    elif feature == "ai_explain":
        context.user_data["state"] = AI_EXPLAIN_STATE
        await query.edit_message_text("🧠 Send any topic/concept to explain like you're 5:")
    elif feature == "ai_roast":
        context.user_data["state"] = AI_ROAST_STATE
        await query.edit_message_text("🔥 Send a name or bio to get ROASTED by AI:")
    elif feature == "ai_business":
        context.user_data["state"] = AI_BUSINESS_STATE
        await query.edit_message_text("💼 Describe your business idea for AI analysis:")
    elif feature == "ai_seo":
        context.user_data["state"] = AI_SEO_STATE
        await query.edit_message_text("📈 Send a keyword or topic for SEO analysis:")
    elif feature == "ai_caption":
        context.user_data["state"] = AI_CAPTION_STATE
        await query.edit_message_text("📸 Describe your photo/post for AI caption:")

    # ===== POWER TOOLS =====
    elif feature == "temp_mail":
        await handle_temp_mail(query)
        context.user_data["state"] = None
    elif feature == "crypto_price":
        context.user_data["state"] = CRYPTO_PRICE_STATE
        await query.edit_message_text("💰 Send crypto name (e.g., bitcoin, ethereum, solana):")
    elif feature == "timezone_convert":
        context.user_data["state"] = TIMEZONE_STATE
        await query.edit_message_text("🕐 Send timezone (e.g., US/Eastern, Asia/Kolkata, Europe/London):")
    elif feature == "color_palette":
        context.user_data["state"] = COLOR_PALETTE_STATE
        await query.edit_message_text("🎨 Send a color name or hex code for palette generation:")
    elif feature == "json_formatter":
        context.user_data["state"] = 37
        await query.edit_message_text("📊 Send JSON text to format/validate:")
    elif feature == "webhook_tester":
        context.user_data["state"] = 38
        await query.edit_message_text("🔗 Send a URL to test webhook (GET request):")


# ============ MESSAGE HANDLER ============
async def handle_message(update: Update, context) -> None:
    current_state = context.user_data.get("state")

    state_handlers = {
        URL_SHORTENER_STATE: url_shortener_handler,
        QR_CODE_GENERATOR_STATE: qr_code_generator_handler,
        DOWNLOADER_STATE: downloader_handler,
        CALCULATOR_STATE: calculator_handler,
        UNIT_CONVERTER_STATE: unit_converter_handler,
        WEATHER_CHECK_STATE: weather_check_handler,
        PASSWORD_GENERATOR_STATE: password_generator_handler,
        NOTES_STATE: notes_handler,
        WEBSITE_TRAFFIC_STATE: website_traffic_handler,
        IP_LOOKUP_STATE: ip_lookup_handler,
        PHONE_LOOKUP_STATE: phone_lookup_handler,
        EMAIL_CHECK_STATE: email_check_handler,
        WHOIS_LOOKUP_STATE: whois_lookup_handler,
        PORT_SCANNER_STATE: port_scanner_handler,
        HEADER_ANALYZER_STATE: header_analyzer_handler,
        HASH_GENERATOR_STATE: hash_generator_handler,
        BASE64_STATE: base64_handler,
        DNS_LOOKUP_STATE: dns_lookup_handler,
        SUBDOMAIN_FINDER_STATE: subdomain_finder_handler,
        LINK_ANALYZER_STATE: link_analyzer_handler,
        BROADCAST_STATE: broadcast_message_handler,
        AI_ASK_STATE: ai_ask_handler,
        AI_IMAGE_STATE: ai_image_handler,
        AI_CODE_STATE: ai_code_handler,
        AI_TRANSLATE_STATE: ai_translate_handler,
        AI_SUMMARIZE_STATE: ai_summarize_handler,
        AI_REWRITE_STATE: ai_rewrite_handler,
        AI_EXPLAIN_STATE: ai_explain_handler,
        AI_ROAST_STATE: ai_roast_handler,
        AI_BUSINESS_STATE: ai_business_handler,
        AI_SEO_STATE: ai_seo_handler,
        AI_CAPTION_STATE: ai_caption_handler,
        TEMP_MAIL_STATE: temp_mail_handler,
        CRYPTO_PRICE_STATE: crypto_price_handler,
        TIMEZONE_STATE: timezone_handler,
        COLOR_PALETTE_STATE: color_palette_handler,
        37: json_formatter_handler,
        38: webhook_tester_handler,
    }

    handler = state_handlers.get(current_state)
    if handler:
        await handler(update, context)
    else:
        await update.message.reply_text("Use /start to see all features.", reply_markup=get_main_menu_keyboard())

    context.user_data["state"] = None

# ============ AI ASK HANDLER ============
async def ai_ask_handler(update: Update, context) -> None:
    question = update.message.text
    await update.message.reply_text("🤖 Thinking...")
    answer = nvidia_ai_chat(question)
    await update.message.reply_text(f"🤖 AI Response:\n\n{answer}", reply_markup=get_main_menu_keyboard())

# ============ ORIGINAL FEATURE HANDLERS ============
async def url_shortener_handler(update: Update, context) -> None:
    original_url = update.message.text
    try:
        response = requests.get(f"https://is.gd/create.php?format=json&url={original_url}", timeout=10)
        response.raise_for_status()
        shortened_url = response.json()["shorturl"]
        await update.message.reply_text(f"🔗 Shortened URL:\n{shortened_url}", reply_markup=get_main_menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_main_menu_keyboard())

async def qr_code_generator_handler(update: Update, context) -> None:
    data = update.message.text
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={data}"
    await update.message.reply_photo(qr_code_url, caption="📸 Your QR Code!", reply_markup=get_main_menu_keyboard())

async def downloader_handler(update: Update, context) -> None:
    link = update.message.text
    output_path = f"/tmp/{update.effective_user.id}_download"
    try:
        await update.message.reply_text("⬇️ Downloading... Please wait.")
        os.makedirs(output_path, exist_ok=True)
        command = ["yt-dlp", "-f", "best[filesize<50M]", "-o", f"{output_path}/%(title)s.%(ext)s", link]
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            downloaded_files = [f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f))]
            if downloaded_files:
                file_path = os.path.join(output_path, downloaded_files[0])
                file_size = os.path.getsize(file_path)
                if file_size < 50 * 1024 * 1024:
                    await update.message.reply_document(document=open(file_path, 'rb'), caption="✅ Download complete!", reply_markup=get_main_menu_keyboard())
                else:
                    await update.message.reply_text("❌ File too large for Telegram (>50MB).", reply_markup=get_main_menu_keyboard())
            else:
                await update.message.reply_text("❌ No file found.", reply_markup=get_main_menu_keyboard())
        else:
            error_msg = stderr.decode()[:500]
            await update.message.reply_text(f"❌ Failed:\n{error_msg}", reply_markup=get_main_menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_main_menu_keyboard())
    finally:
        if os.path.exists(output_path):
            for f in os.listdir(output_path):
                os.remove(os.path.join(output_path, f))
            os.rmdir(output_path)

async def calculator_handler(update: Update, context) -> None:
    expression = update.message.text
    try:
        cleaned = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        result = eval(cleaned)
        await update.message.reply_text(f"🔢 Result: {result}", reply_markup=get_main_menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_main_menu_keyboard())

async def unit_converter_handler(update: Update, context) -> None:
    text = update.message.text.lower()
    match = re.match(r"^(\d+(\.\d+)?)\s*([a-zA-Z]+)\s+to\s+([a-zA-Z]+)$", text)
    if not match:
        await update.message.reply_text("Format: VALUE UNIT1 to UNIT2\nExample: 10 km to miles", reply_markup=get_main_menu_keyboard())
        return
    value, _, unit1, unit2 = match.groups()
    value = float(value)
    conversions = {
        ("km", "miles"): lambda v: v * 0.621371,
        ("miles", "km"): lambda v: v * 1.60934,
        ("c", "f"): lambda v: (v * 9/5) + 32,
        ("f", "c"): lambda v: (v - 32) * 5/9,
        ("kg", "lbs"): lambda v: v * 2.20462,
        ("lbs", "kg"): lambda v: v * 0.453592,
        ("m", "ft"): lambda v: v * 3.28084,
        ("ft", "m"): lambda v: v * 0.3048,
        ("cm", "inch"): lambda v: v * 0.393701,
        ("inch", "cm"): lambda v: v * 2.54,
        ("l", "gal"): lambda v: v * 0.264172,
        ("gal", "l"): lambda v: v * 3.78541,
    }
    converter = conversions.get((unit1, unit2))
    if converter:
        result = converter(value)
        await update.message.reply_text(f"🔄 {value} {unit1} = {result:.2f} {unit2}", reply_markup=get_main_menu_keyboard())
    else:
        await update.message.reply_text(f"Can't convert {unit1} to {unit2}. Supported: km/miles, c/f, kg/lbs, m/ft, cm/inch, l/gal", reply_markup=get_main_menu_keyboard())

async def weather_check_handler(update: Update, context) -> None:
    city = update.message.text
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3", timeout=10)
        response.raise_for_status()
        await update.message.reply_text(f"☁️ {response.text}", reply_markup=get_main_menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_main_menu_keyboard())

async def password_generator_handler(update: Update, context) -> None:
    try:
        length = int(update.message.text)
        if 6 <= length <= 50:
            password = "".join(random.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(length))
            await update.message.reply_text(f"🔐 Password:\n{password}", reply_markup=get_main_menu_keyboard())
        else:
            await update.message.reply_text("Length must be 6-50.", reply_markup=get_main_menu_keyboard())
    except ValueError:
        await update.message.reply_text("Send a number.", reply_markup=get_main_menu_keyboard())

async def notes_handler(update: Update, context) -> None:
    user_id = update.effective_user.id
    note_text = update.message.text
    add_note(user_id, note_text)
    await update.message.reply_text("📝 Saved! Use /viewnotes to view all.", reply_markup=get_main_menu_keyboard())

async def view_notes_command(update: Update, context) -> None:
    user_id = update.effective_user.id
    notes = get_notes(user_id)
    if notes:
        notes_text = "📝 Your Notes:\n" + "\n".join([f"{i+1}. {note}" for i, note in enumerate(notes)])
        await update.message.reply_text(notes_text, reply_markup=get_main_menu_keyboard())
    else:
        await update.message.reply_text("No notes saved.", reply_markup=get_main_menu_keyboard())
    context.user_data["state"] = None

async def website_traffic_handler(update: Update, context) -> None:
    url = update.message.text
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "N/A"
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        desc = desc_tag["content"] if desc_tag and "content" in desc_tag.attrs else "N/A"
        scripts = len(soup.find_all('script'))
        links = len(soup.find_all('a'))
        images = len(soup.find_all('img'))
        await update.message.reply_text(
            f"🌐 Site Analysis: {url}\n\n"
            f"📌 Title: {title}\n"
            f"📝 Description: {desc[:200]}\n"
            f"📜 Scripts: {scripts}\n"
            f"🔗 Links: {links}\n"
            f"🖼️ Images: {images}\n"
            f"📊 Page Size: {len(response.content) / 1024:.1f} KB",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_main_menu_keyboard())

# ============ DARK TOOL HANDLERS ============

async def ip_lookup_handler(update: Update, context) -> None:
    ip = update.message.text.strip()
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query", timeout=10)
        data = response.json()
        if data.get("status") == "success":
            result = (
                f"🎯 IP TRACE RESULT\n\n"
                f"🌐 IP: {data.get('query', 'N/A')}\n"
                f"🏳️ Country: {data.get('country', 'N/A')} ({data.get('countryCode', '')})\n"
                f"🏙️ City: {data.get('city', 'N/A')}\n"
                f"📍 Region: {data.get('regionName', 'N/A')}\n"
                f"📮 ZIP: {data.get('zip', 'N/A')}\n"
                f"📡 ISP: {data.get('isp', 'N/A')}\n"
                f"🏢 Org: {data.get('org', 'N/A')}\n"
                f"🔢 AS: {data.get('as', 'N/A')}\n"
                f"🕐 Timezone: {data.get('timezone', 'N/A')}\n"
                f"📌 Lat/Lon: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}"
            )
        else:
            result = f"❌ Failed: {data.get('message', 'Invalid IP')}"
        await update.message.reply_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def phone_lookup_handler(update: Update, context) -> None:
    phone = update.message.text.strip()
    try:
        clean = re.sub(r'[^0-9+]', '', phone)
        country_codes = {
            "+1": "USA/Canada", "+44": "UK", "+91": "India",
            "+86": "China", "+81": "Japan", "+49": "Germany",
            "+33": "France", "+7": "Russia", "+61": "Australia",
            "+55": "Brazil", "+92": "Pakistan", "+880": "Bangladesh",
            "+234": "Nigeria", "+27": "South Africa", "+82": "South Korea",
            "+39": "Italy", "+34": "Spain", "+90": "Turkey",
            "+62": "Indonesia", "+60": "Malaysia", "+66": "Thailand",
            "+84": "Vietnam", "+20": "Egypt", "+971": "UAE",
            "+966": "Saudi Arabia", "+63": "Philippines",
        }
        detected = "Unknown"
        for code, name in sorted(country_codes.items(), key=lambda x: -len(x[0])):
            if clean.startswith(code):
                detected = name
                break
        result = (
            f"📱 PHONE LOOKUP\n\n"
            f"📞 Number: {phone}\n"
            f"🏳️ Country: {detected}\n"
            f"📏 Digits: {len(re.sub(r'[^0-9]', '', phone))}\n"
            f"✅ Format: {'Valid' if len(re.sub(r'[^0-9]', '', phone)) >= 10 else 'Invalid'}"
        )
        await update.message.reply_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def email_check_handler(update: Update, context) -> None:
    email = update.message.text.strip()
    try:
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            await update.message.reply_text("❌ Invalid email format.", reply_markup=get_dark_tools_keyboard())
            return
        response = requests.get(f"https://emailrep.io/{email}", headers={"User-Agent": "GeniusKex Bot"}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            reputation = data.get("reputation", "N/A")
            suspicious = data.get("suspicious", "N/A")
            references = data.get("references", 0)
            details = data.get("details", {})
            breached = details.get("data_breach", False)
            malicious = details.get("malicious_activity", False)
            spam = details.get("spam", False)
            profiles = details.get("profiles", [])
            result = (
                f"📧 EMAIL INTELLIGENCE\n\n"
                f"📩 Email: {email}\n"
                f"⭐ Reputation: {reputation}\n"
                f"🚨 Suspicious: {suspicious}\n"
                f"💀 Data Breach: {'YES ⚠️' if breached else 'No'}\n"
                f"🦠 Malicious Activity: {'YES ⚠️' if malicious else 'No'}\n"
                f"📨 Spam: {'YES' if spam else 'No'}\n"
                f"🔗 References: {references}\n"
                f"👤 Profiles: {', '.join(profiles) if profiles else 'None found'}"
            )
        else:
            domain = email.split('@')[1]
            try:
                socket.getaddrinfo(domain, 25)
                valid = True
            except Exception:
                valid = False
            result = (
                f"📧 EMAIL CHECK\n\n"
                f"📩 Email: {email}\n"
                f"🌐 Domain: {domain}\n"
                f"✅ Domain Valid: {'Yes' if valid else 'No'}\n"
                f"💡 Tip: Use haveibeenpwned.com for full breach data"
            )
        await update.message.reply_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def whois_lookup_handler(update: Update, context) -> None:
    domain = update.message.text.strip()
    if python_whois is None:
        await update.message.reply_text("WHOIS module not available.", reply_markup=get_dark_tools_keyboard())
        return
    try:
        w = python_whois.whois(domain)
        result = (
            f"🕵️ WHOIS LOOKUP\n\n"
            f"🌐 Domain: {domain}\n"
            f"📛 Registrar: {w.registrar or 'N/A'}\n"
            f"📅 Created: {w.creation_date or 'N/A'}\n"
            f"📅 Expires: {w.expiration_date or 'N/A'}\n"
            f"📅 Updated: {w.updated_date or 'N/A'}\n"
            f"🏳️ Country: {w.country or 'N/A'}\n"
            f"🏢 Org: {w.org or 'N/A'}\n"
            f"📧 Emails: {w.emails or 'N/A'}\n"
            f"🔤 Name Servers: {', '.join(w.name_servers) if w.name_servers else 'N/A'}\n"
            f"🔒 Status: {w.status[0] if isinstance(w.status, list) and w.status else w.status or 'N/A'}"
        )
        await update.message.reply_text(result[:4000], reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def port_scanner_handler(update: Update, context) -> None:
    target = update.message.text.strip()
    await update.message.reply_text(f"🔓 Scanning top ports on {target}... Please wait.")
    try:
        common_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
            993: "IMAPS", 995: "POP3S", 3306: "MySQL", 3389: "RDP",
            5432: "PostgreSQL", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
            27017: "MongoDB", 9200: "Elasticsearch"
        }
        try:
            ip = socket.gethostbyname(target)
        except Exception:
            ip = target
        open_ports = []
        for port, service in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                r = sock.connect_ex((ip, port))
                if r == 0:
                    open_ports.append(f"  ✅ {port} - {service} [OPEN]")
                sock.close()
            except Exception:
                pass
        if open_ports:
            result = f"🔓 PORT SCAN: {target} ({ip})\n\n" + "\n".join(open_ports) + f"\n\n📊 {len(open_ports)}/{len(common_ports)} ports open"
        else:
            result = f"🔓 PORT SCAN: {target}\n\n❌ No open ports found (or host is down/filtered)"
        await update.message.reply_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def header_analyzer_handler(update: Update, context) -> None:
    url = update.message.text.strip()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        headers = response.headers
        security_headers = {
            "Strict-Transport-Security": "HSTS",
            "Content-Security-Policy": "CSP",
            "X-Frame-Options": "Clickjack Protection",
            "X-Content-Type-Options": "MIME Sniffing",
            "X-XSS-Protection": "XSS Protection",
            "Referrer-Policy": "Referrer Policy",
            "Permissions-Policy": "Permissions",
        }
        result = f"🛡️ HEADER ANALYSIS: {url}\n\n"
        result += f"📡 Status: {response.status_code}\n"
        result += f"🖥️ Server: {headers.get('Server', 'Hidden')}\n"
        result += f"⚡ Powered By: {headers.get('X-Powered-By', 'Hidden')}\n\n"
        result += "🔒 Security Headers:\n"
        score = 0
        for header, name in security_headers.items():
            if header in headers:
                result += f"  ✅ {name}: Present\n"
                score += 1
            else:
                result += f"  ❌ {name}: MISSING\n"
        grade = "A+" if score >= 6 else "A" if score >= 5 else "B" if score >= 4 else "C" if score >= 3 else "D" if score >= 2 else "F"
        result += f"\n📊 Security Score: {score}/{len(security_headers)} (Grade: {grade})"
        await update.message.reply_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def hash_generator_handler(update: Update, context) -> None:
    text = update.message.text
    try:
        text_bytes = text.encode('utf-8')
        result = (
            f"🧬 HASH RESULTS\n\n"
            f"📝 Input: {text[:50]}{'...' if len(text) > 50 else ''}\n\n"
            f"MD5:\n{hashlib.md5(text_bytes).hexdigest()}\n\n"
            f"SHA1:\n{hashlib.sha1(text_bytes).hexdigest()}\n\n"
            f"SHA256:\n{hashlib.sha256(text_bytes).hexdigest()}\n\n"
            f"SHA512:\n{hashlib.sha512(text_bytes).hexdigest()}"
        )
        await update.message.reply_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def base64_handler(update: Update, context) -> None:
    text = update.message.text
    try:
        if text.lower().startswith("encode:"):
            data = text[7:].strip()
            encoded = base64.b64encode(data.encode()).decode()
            result = f"🔀 BASE64 ENCODED:\n\n{encoded}"
        elif text.lower().startswith("decode:"):
            data = text[7:].strip()
            decoded = base64.b64decode(data).decode()
            result = f"🔀 BASE64 DECODED:\n\n{decoded}"
        else:
            encoded = base64.b64encode(text.encode()).decode()
            decoded_attempt = ""
            try:
                decoded_attempt = base64.b64decode(text).decode()
            except Exception:
                pass
            result = f"🔀 BASE64 RESULTS\n\nEncoded:\n{encoded}"
            if decoded_attempt:
                result += f"\n\nDecoded (if base64):\n{decoded_attempt}"
        await update.message.reply_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def dns_lookup_handler(update: Update, context) -> None:
    domain = update.message.text.strip()
    try:
        result = f"🌍 DNS LOOKUP: {domain}\n\n"
        try:
            ips = socket.getaddrinfo(domain, None, socket.AF_INET)
            a_records = list(set([ip[4][0] for ip in ips]))
            result += f"📌 A Records:\n" + "\n".join([f"  {ip}" for ip in a_records]) + "\n\n"
        except Exception:
            result += "📌 A Records: Not found\n\n"
        try:
            ips6 = socket.getaddrinfo(domain, None, socket.AF_INET6)
            aaaa_records = list(set([ip[4][0] for ip in ips6]))
            result += f"📌 AAAA Records:\n" + "\n".join([f"  {ip}" for ip in aaaa_records[:3]]) + "\n\n"
        except Exception:
            result += "📌 AAAA Records: Not found\n\n"
        try:
            dns_resp = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=5)
            mx_data = dns_resp.json()
            if "Answer" in mx_data:
                mx_records = [a["data"] for a in mx_data["Answer"]]
                result += f"📧 MX Records:\n" + "\n".join([f"  {mx}" for mx in mx_records[:5]]) + "\n\n"
        except Exception:
            pass
        try:
            dns_resp = requests.get(f"https://dns.google/resolve?name={domain}&type=NS", timeout=5)
            ns_data = dns_resp.json()
            if "Answer" in ns_data:
                ns_records = [a["data"] for a in ns_data["Answer"]]
                result += f"🔤 NS Records:\n" + "\n".join([f"  {ns}" for ns in ns_records[:5]]) + "\n\n"
        except Exception:
            pass
        try:
            dns_resp = requests.get(f"https://dns.google/resolve?name={domain}&type=TXT", timeout=5)
            txt_data = dns_resp.json()
            if "Answer" in txt_data:
                txt_records = [a["data"] for a in txt_data["Answer"]]
                result += f"📜 TXT Records:\n" + "\n".join([f"  {txt[:100]}" for txt in txt_records[:3]])
        except Exception:
            pass
        await update.message.reply_text(result[:4000], reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def handle_fake_identity(query) -> None:
    try:
        response = requests.get("https://randomuser.me/api/", timeout=10)
        data = response.json()["results"][0]
        name = f"{data['name']['first']} {data['name']['last']}"
        result = (
            f"👤 FAKE IDENTITY GENERATED\n\n"
            f"📛 Name: {name}\n"
            f"📧 Email: {data['email']}\n"
            f"📱 Phone: {data['phone']}\n"
            f"📞 Cell: {data['cell']}\n"
            f"🎂 DOB: {data['dob']['date'][:10]} (Age: {data['dob']['age']})\n"
            f"🏠 Address: {data['location']['street']['number']} {data['location']['street']['name']}\n"
            f"🏙️ City: {data['location']['city']}, {data['location']['state']}\n"
            f"🏳️ Country: {data['location']['country']} ({data['nat']})\n"
            f"📮 Postcode: {data['location']['postcode']}\n"
            f"👤 Username: {data['login']['username']}\n"
            f"🔑 Password: {data['login']['password']}"
        )
        await query.edit_message_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await query.edit_message_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def subdomain_finder_handler(update: Update, context) -> None:
    domain = update.message.text.strip()
    await update.message.reply_text(f"🕸️ Finding subdomains for {domain}...")
    try:
        response = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=15)
        if response.status_code == 200:
            data = response.json()
            subdomains = sorted(list(set([entry['name_value'] for entry in data])))
            if subdomains:
                sub_list = "\n".join([f"  • {s}" for s in subdomains[:30]])
                result = f"🕸️ SUBDOMAINS: {domain}\n\n{sub_list}\n\n📊 Total found: {len(subdomains)}"
                if len(subdomains) > 30:
                    result += f" (showing 30/{len(subdomains)})"
            else:
                result = f"No subdomains found for {domain}"
        else:
            result = "Error fetching subdomains."
        await update.message.reply_text(result[:4000], reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

async def link_analyzer_handler(update: Update, context) -> None:
    url = update.message.text.strip()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, allow_redirects=True)
        final_url = response.url
        redirects = len(response.history)
        ssl = final_url.startswith("https")
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = len(soup.find_all('form'))
        inputs = len(soup.find_all('input'))
        password_fields = len(soup.find_all('input', {'type': 'password'}))
        external_links = len([a for a in soup.find_all('a', href=True) if a['href'].startswith('http') and url.split('/')[2] not in a['href']])
        scripts = len(soup.find_all('script'))
        iframes = len(soup.find_all('iframe'))
        risk_score = 0
        risks = []
        if not ssl:
            risk_score += 3; risks.append("❌ No SSL/HTTPS")
        if password_fields > 0:
            risk_score += 2; risks.append(f"⚠️ {password_fields} password field(s)")
        if redirects > 2:
            risk_score += 2; risks.append(f"⚠️ {redirects} redirects")
        if iframes > 0:
            risk_score += 1; risks.append(f"⚠️ {iframes} iframe(s)")
        if external_links > 20:
            risk_score += 1; risks.append(f"⚠️ {external_links} external links")
        verdict = "✅ SAFE" if risk_score == 0 else "⚠️ LOW RISK" if risk_score <= 2 else "🟠 MEDIUM RISK" if risk_score <= 4 else "🔴 HIGH RISK"
        result = (
            f"🔍 LINK ANALYSIS\n\n"
            f"🔗 URL: {url}\n"
            f"🎯 Final URL: {final_url}\n"
            f"🔀 Redirects: {redirects}\n"
            f"🔒 SSL: {'Yes' if ssl else 'No'}\n"
            f"📊 Status: {response.status_code}\n\n"
            f"📋 Page Analysis:\n"
            f"  Forms: {forms} | Inputs: {inputs}\n"
            f"  Password Fields: {password_fields}\n"
            f"  Scripts: {scripts} | iFrames: {iframes}\n"
            f"  External Links: {external_links}\n\n"
            f"🎯 Verdict: {verdict}\n"
        )
        if risks:
            result += "⚠️ Risks:\n" + "\n".join([f"  {r}" for r in risks])
        await update.message.reply_text(result, reply_markup=get_dark_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_dark_tools_keyboard())

# ============ BROADCAST ============
async def broadcast(update: Update, context) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    message_to_send = " ".join(context.args)
    users = get_all_users()
    sent_count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Broadcast:\n\n{message_to_send}")
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.warning(f"Broadcast fail {uid}: {e}")
    await update.message.reply_text(f"✅ Sent to {sent_count}/{len(users)} users.", reply_markup=get_main_menu_keyboard())

async def broadcast_message_handler(update: Update, context) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Not authorized.")
        return
    message_to_send = update.message.text
    users = get_all_users()
    sent_count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Broadcast:\n\n{message_to_send}")
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.warning(f"Broadcast fail {uid}: {e}")
    await update.message.reply_text(f"✅ Sent to {sent_count}/{len(users)} users.", reply_markup=get_main_menu_keyboard())

# ============ AI TOOLS 2026 HANDLERS ============

async def ai_image_handler(update: Update, context) -> None:
    desc = update.message.text
    await update.message.reply_text("🎨 Generating image prompt...")
    prompt = f"Create a detailed, professional AI image generation prompt for: {desc}. Include style, lighting, composition, mood, and technical details. Output ONLY the prompt, nothing else."
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"🎨 AI Image Prompt:\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_code_handler(update: Update, context) -> None:
    desc = update.message.text
    await update.message.reply_text("💻 Generating code...")
    prompt = f"Write clean, production-ready code for: {desc}. Include comments. Output ONLY the code with brief explanation."
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"💻 AI Code:\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_translate_handler(update: Update, context) -> None:
    text = update.message.text
    await update.message.reply_text("🌐 Translating...")
    parts = text.split(" ", 1)
    if len(parts) >= 2:
        target_lang = parts[0]
        content = parts[1]
    else:
        target_lang = "English"
        content = text
    prompt = f"Translate the following text to {target_lang}. Output ONLY the translation:\n{content}"
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"🌐 Translation ({target_lang}):\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_summarize_handler(update: Update, context) -> None:
    text = update.message.text
    await update.message.reply_text("📋 Summarizing...")
    prompt = f"Summarize the following text in 3-5 bullet points. Be concise and capture key points:\n\n{text}"
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"📋 Summary:\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_rewrite_handler(update: Update, context) -> None:
    text = update.message.text
    await update.message.reply_text("✍️ Rewriting...")
    prompt = f"Rewrite the following text to be more professional, engaging, and polished. Keep the same meaning:\n\n{text}"
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"✍️ Rewritten:\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_explain_handler(update: Update, context) -> None:
    topic = update.message.text
    await update.message.reply_text("🧠 Explaining...")
    prompt = f"Explain '{topic}' like I'm 5 years old. Use simple analogies and examples. Make it fun and easy to understand."
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"🧠 Explanation:\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_roast_handler(update: Update, context) -> None:
    target = update.message.text
    await update.message.reply_text("🔥 Preparing roast...")
    prompt = f"Give a savage but funny roast of: {target}. Be creative, witty, and brutal. 5 roast lines. Keep it humorous not hateful."
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"🔥 ROASTED:\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_business_handler(update: Update, context) -> None:
    idea = update.message.text
    await update.message.reply_text("💼 Analyzing business idea...")
    prompt = f"Analyze this business idea: {idea}\n\nProvide: 1) Market potential (1-10) 2) Revenue model suggestions 3) Top 3 risks 4) Competitive advantage needed 5) First 3 steps to start. Be direct and actionable."
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"💼 Business Analysis:\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_seo_handler(update: Update, context) -> None:
    keyword = update.message.text
    await update.message.reply_text("📈 Analyzing SEO...")
    prompt = f"SEO analysis for keyword/topic: {keyword}\n\nProvide: 1) 10 related long-tail keywords 2) Title tag suggestion 3) Meta description 4) Content outline (H2 headings) 5) Difficulty estimate (easy/medium/hard). Format clearly."
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"📈 SEO Analysis:\n\n{result}", reply_markup=get_ai_tools_keyboard())

async def ai_caption_handler(update: Update, context) -> None:
    desc = update.message.text
    await update.message.reply_text("📸 Generating captions...")
    prompt = f"Generate 5 viral social media captions for: {desc}\n\nInclude: 1) Instagram style (with emojis + hashtags) 2) Twitter/X style (short, punchy) 3) LinkedIn style (professional) 4) TikTok style (trendy) 5) YouTube title style (clickbait but honest). Make them engaging and shareable."
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"📸 Captions:\n\n{result}", reply_markup=get_ai_tools_keyboard())

# ============ POWER TOOL HANDLERS ============

async def handle_temp_mail(query) -> None:
    try:
        response = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=3", timeout=10)
        emails = response.json()
        email_list = "\n".join([f"📧 {e}" for e in emails])
        await query.edit_message_text(f"📧 Temporary Emails (valid for 1 hour):\n\n{email_list}\n\nUse these for signups!", reply_markup=get_power_tools_keyboard())
    except Exception as e:
        await query.edit_message_text(f"Error: {e}", reply_markup=get_power_tools_keyboard())

async def temp_mail_handler(update: Update, context) -> None:
    await update.message.reply_text("Use the Temp Mail button for instant emails.", reply_markup=get_power_tools_keyboard())

async def crypto_price_handler(update: Update, context) -> None:
    coin = update.message.text.strip().lower()
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr,eur&include_24hr_change=true&include_market_cap=true", timeout=10)
        data = response.json()
        if coin in data:
            d = data[coin]
            result = (
                f"💰 {coin.upper()} Price\n\n"
                f"💵 USD: ${d.get('usd', 'N/A'):,.2f}\n"
                f"💶 EUR: €{d.get('eur', 'N/A'):,.2f}\n"
                f"🇮🇳 INR: ₹{d.get('inr', 'N/A'):,.2f}\n"
                f"📊 24h Change: {d.get('usd_24h_change', 0):.2f}%\n"
                f"🏦 Market Cap: ${d.get('usd_market_cap', 0):,.0f}"
            )
        else:
            result = f"❌ Coin '{coin}' not found. Try: bitcoin, ethereum, solana, dogecoin"
        await update.message.reply_text(result, reply_markup=get_power_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_power_tools_keyboard())

async def timezone_handler(update: Update, context) -> None:
    tz = update.message.text.strip()
    try:
        response = requests.get(f"https://worldtimeapi.org/api/timezone/{tz}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            result = (
                f"🕐 Timezone: {data['timezone']}\n\n"
                f"📅 Date/Time: {data['datetime'][:19]}\n"
                f"📍 UTC Offset: {data['utc_offset']}\n"
                f"☀️ Day of Year: {data['day_of_year']}\n"
                f"📆 Week: {data['week_number']}"
            )
        else:
            result = f"❌ Invalid timezone. Examples: US/Eastern, Asia/Kolkata, Europe/London\nFull list: worldtimeapi.org/api/timezone"
        await update.message.reply_text(result, reply_markup=get_power_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Error: {e}", reply_markup=get_power_tools_keyboard())

async def color_palette_handler(update: Update, context) -> None:
    color = update.message.text.strip()
    await update.message.reply_text("🎨 Generating palette...")
    prompt = f"Generate a color palette based on '{color}'. Provide 5 complementary colors with: 1) HEX code 2) RGB values 3) Color name 4) Best use case (web, print, etc). Format as a clean list."
    result = nvidia_ai_chat(prompt)
    await update.message.reply_text(f"🎨 Color Palette:\n\n{result}", reply_markup=get_power_tools_keyboard())

async def json_formatter_handler(update: Update, context) -> None:
    text = update.message.text
    try:
        parsed = json.loads(text)
        formatted = json.dumps(parsed, indent=2)
        if len(formatted) > 4000:
            formatted = formatted[:4000] + "\n... (truncated)"
        await update.message.reply_text(f"📊 Formatted JSON:\n\n{formatted}", reply_markup=get_power_tools_keyboard())
    except json.JSONDecodeError as e:
        await update.message.reply_text(f"❌ Invalid JSON:\n{str(e)}", reply_markup=get_power_tools_keyboard())

async def webhook_tester_handler(update: Update, context) -> None:
    url = update.message.text.strip()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'GeniusKexBot/1.0'})
        result = (
            f"🔗 Webhook Test Result\n\n"
            f"📍 URL: {url}\n"
            f"📊 Status: {response.status_code}\n"
            f"⏱️ Response Time: {response.elapsed.total_seconds():.3f}s\n"
            f"📦 Content-Type: {response.headers.get('content-type', 'N/A')}\n"
            f"📏 Size: {len(response.content)} bytes\n"
            f"🔒 HTTPS: {'Yes' if url.startswith('https') else 'No'}"
        )
        await update.message.reply_text(result, reply_markup=get_power_tools_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}", reply_markup=get_power_tools_keyboard())

# ============ ERROR HANDLER ============
async def error_handler(update: Update, context) -> None:
    logger.error(f"Error: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("⚠️ An error occurred. Try again or use /start.", reply_markup=get_main_menu_keyboard())
    except Exception:
        pass

# ============ MAIN ============
def main() -> None:
    if not TOKEN:
        logger.error("BOT_TOKEN not set! Set it as environment variable.")
        return

    init_db()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("viewnotes", view_notes_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    logger.info("🚀 GeniusKexBot starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
