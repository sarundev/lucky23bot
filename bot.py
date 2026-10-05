"""JJ7SPORT-style promo bot.

/start replies with a banner image, a caption and three link buttons.

Run with:  python bot.py
"""
from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ChatAction, ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("promo-bot")

# Telegram returns a file_id the first time we upload the banner/voice note;
# reusing it afterwards makes every later /start a metadata-only call instead
# of a full upload.
_banner_file_id: str | None = None
_voice_file_id: str | None = None

_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}


def _banner_is_video() -> bool:
    source = config.BANNER_URL or str(config.BANNER_PATH)
    return Path(source).suffix.lower() in _VIDEO_EXTENSIONS


def quick_menu_keyboard() -> ReplyKeyboardMarkup:
    """The persistent quick-menu button pinned above the message bar."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton(config.BTN_QUICK_CREATE)]],
        resize_keyboard=True,
    )


def main_keyboard() -> InlineKeyboardMarkup:
    """A 2-column grid of link buttons, with the last one full-width."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(config.BTN_REGISTER, url=config.REGISTER_URL),
                InlineKeyboardButton(config.BTN_CHANNEL, url=config.CHANNEL_URL),
            ],
            [InlineKeyboardButton(config.BTN_SUPPORT, url=config.SUPPORT_URL)],
        ]
    )


async def send_promo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the banner + caption + buttons, falling back to text-only."""
    global _banner_file_id

    chat = update.effective_chat
    caption = config.WELCOME_CAPTION
    keyboard = main_keyboard()
    is_video = _banner_is_video()

    # Priority: cached file_id -> remote URL -> local file on disk.
    media = _banner_file_id or config.BANNER_URL or None
    handle = None
    if media is None:
        if config.BANNER_PATH.is_file():
            handle = config.BANNER_PATH.open("rb")
            media = handle
        else:
            log.warning(
                "No banner: BANNER_URL is empty and %s does not exist.",
                config.BANNER_PATH,
            )

    try:
        if media and is_video:
            await chat.send_action(ChatAction.UPLOAD_VIDEO)
            message = await chat.send_video(
                video=media,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                supports_streaming=True,
            )
            if message.video:
                _banner_file_id = message.video.file_id
        elif media:
            await chat.send_action(ChatAction.UPLOAD_PHOTO)
            message = await chat.send_photo(
                photo=media,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
            if message.photo:
                # Cache the largest rendition for subsequent sends.
                _banner_file_id = message.photo[-1].file_id
        else:
            await chat.send_message(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
    except TelegramError as exc:
        log.warning("Banner send failed (%s); falling back to text.", exc)
        _banner_file_id = None
        await chat.send_message(
            caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    finally:
        if handle is not None:
            handle.close()


async def send_voice_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the voice.ogg intro clip, caching its file_id after the first upload."""
    global _voice_file_id

    chat = update.effective_chat
    voice = _voice_file_id
    handle = None
    if voice is None:
        if config.VOICE_PATH.is_file():
            handle = config.VOICE_PATH.open("rb")
            voice = handle
        else:
            log.warning("No voice note: %s does not exist.", config.VOICE_PATH)
            return

    try:
        await chat.send_action(ChatAction.RECORD_VOICE)
        message = await chat.send_voice(voice=voice)
        if message.voice:
            _voice_file_id = message.voice.file_id
    except TelegramError as exc:
        log.warning("Voice send failed (%s)", exc)
        _voice_file_id = None
    finally:
        if handle is not None:
            handle.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    log.info("/start from %s (%s)", user.id, user.full_name)


    await send_promo(update, context)
    await send_voice_note(update, context)
    await update.effective_chat.send_message(
        config.REGISTER_PROMPT.format(url=config.REGISTER_URL),
        disable_web_page_preview=True,
        reply_markup=quick_menu_keyboard(),
    )

    if config.ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                config.ADMIN_CHAT_ID,
                f"👤 New /start: {user.mention_html()} (<code>{user.id}</code>)",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError as exc:
            log.warning("Could not notify admin chat: %s", exc)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html(config.HELP_TEXT)


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_html(
        config.SUPPORT_TEXT,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(config.BTN_SUPPORT, url=config.SUPPORT_URL)]]
        ),
    )


async def quick_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The persistent quick-menu button sends the voice note and agent contact link."""
    await send_voice_note(update, context)
    await update.effective_chat.send_message(
        config.QUICK_CREATE_PROMPT.format(url=config.REGISTER_URL),
        disable_web_page_preview=True,
    )


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Anything the user types just re-shows the promo."""
    await send_promo(update, context)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Handler error", exc_info=context.error)


async def post_init(application: Application) -> None:
    """Register the '/' command list."""
    bot = application.bot

    await bot.set_my_commands(config.BOT_COMMANDS)

    me = await bot.get_me()
    log.info("Running as @%s (id %s)", me.username, me.id)


def main() -> None:
    if not config.BOT_TOKEN:
        sys.exit("BOT_TOKEN is missing. Copy .env.example to .env and fill it in.")

    application = (
        Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(
        MessageHandler(
            filters.Regex(f"^{re.escape(config.BTN_QUICK_CREATE)}$"), quick_create
        )
    )
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    application.add_error_handler(on_error)

    log.info("Polling for updates… (Ctrl-C to stop)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
