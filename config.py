"""Configuration and message content, all in one place.

Edit MESSAGES below to change the wording; edit .env to change tokens/links.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _env(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


BOT_TOKEN = _env("BOT_TOKEN")

BANNER_URL = _env("BANNER_URL")
BANNER_PATH = BASE_DIR / _env("BANNER_PATH", "assets/pic1.jpg")

VOICE_PATH = BASE_DIR / _env("VOICE_PATH", "assets/voice.ogg")

REGISTER_URL = _env("REGISTER_URL", "https://t.me/v99somnangshop")
CHANNEL_URL = _env("CHANNEL_URL", "https://t.me/v99somnangshop")
SUPPORT_URL = _env("SUPPORT_URL", "https://t.me/v99somnangshop")

_admin = _env("ADMIN_CHAT_ID")
ADMIN_CHAT_ID = int(_admin) if _admin.lstrip("-").isdigit() else None

# ── Text shown to users (HTML parse mode) ───────────────────────────────
WELCOME_CAPTION = (
    "<b>💥SB24 វេទិកាកាស៊ីណូអនឡាញល្អផ្ដាច់គេនៅកម្ពុជា! មាន់ជល់​ ចាក់បាល់​ បៀរ​ ឡូ​តូ8888⚡️</b>\n"

)

REGISTER_PROMPT = "🔥ចុះឈ្មោះឥឡូវនេះ {url}"
QUICK_CREATE_PROMPT = "បើកអាខោន: {url}"

HELP_TEXT = (
    "<b>ជំនួយ / Help</b>\n"
    "\n"
    "/start — ទទួលបានតំណភ្ជាប់ចុះឈ្មោះ\n"
    "/help — មើលបញ្ជីពាក្យបញ្ជា\n"
    "/support — ទាក់ទងផ្នែកបម្រើអតិថិជន"
)

SUPPORT_TEXT = (
    "ក្រុមការងារបម្រើអតិថិជនរបស់យើងបម្រើសេវា <b>24/7</b>។\n"
    "សូមចុចប៊ូតុងខាងក្រោមដើម្បីជជែកផ្ទាល់។"
)

# ── Inline button labels ────────────────────────────────────────────────
BTN_REGISTER = "📲បើកអាខោនរហ័ស"
BTN_CHANNEL = "🧧អតិថិជនថ្មីថែម100%"
BTN_DEPOSIT = "⚡️ដាក់ដកលុយរហ័ស"
BTN_SUPPORT = "📲ចុះឈ្មោះបើកអាខោន២៤ម៉ោង🎰"

# ── Persistent quick-menu buttons (shown above the message bar) ─────────
BTN_QUICK_CREATE = "បើកអាខោន២៤ម៉ោង"

# ── Commands shown in the "/" menu ──────────────────────────────────────
BOT_COMMANDS = [
    ("start", "ចាប់ផ្តើម / Start"),
]
