# Telegram Promo Bot

Replicates the JJ7SPORT flow: `/start` → banner image + Khmer caption + three
link buttons, with a Mini-App button pinned in the bottom-left of the chat.

## Files

| File | Purpose |
|---|---|
| `bot.py` | Handlers, keyboard, startup (`post_init`) |
| `config.py` | All text/labels; reads secrets from `.env` |
| `.env.example` | Template for your token and links |
| `assets/banner.jpg` | The promo image sent with `/start` |

## Setup

1. **Create the bot** — message [@BotFather](https://t.me/BotFather), send
   `/newbot`, follow the prompts, copy the token.

2. **Install** (Python 3.9+):

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

3. **Configure**:

```bash
cp .env.example .env
```

Then edit `.env` and set at minimum `BOT_TOKEN`, `REGISTER_URL`,
`CHANNEL_URL`, `SUPPORT_URL`.

4. **Add your artwork** — drop your 1280×720-ish image at `assets/banner.jpg`
   (or set `BANNER_URL` to an https link and leave the file alone).

5. **Run**:

```bash
python bot.py
```

Open the bot in Telegram and send `/start`.

## Customising

- **Wording / button labels** — everything is in `config.py` under
  `WELCOME_CAPTION`, `BTN_REGISTER`, `BTN_CHANNEL`, `BTN_SUPPORT`. Captions use
  HTML (`<b>`, `<i>`, `<a href="">`), max 1024 characters.
- **More buttons** — add rows to `main_keyboard()` in `bot.py`. Each inner list
  is one row, so two buttons in one list sit side by side.
- **New command** — add a handler in `main()` and a line in `BOT_COMMANDS`.

## Notes

- The banner is uploaded once; the returned `file_id` is cached in memory and
  reused, so restarts re-upload but individual `/start`s do not.
- If the image fails to send for any reason, the bot degrades to a text-only
  message with the same buttons rather than failing silently.
- Long polling needs no public server. For webhooks on a VPS, swap
  `run_polling()` for `run_webhook()`.

## Running it as a service (optional, Linux)

```bash
sudo tee /etc/systemd/system/promo-bot.service >/dev/null <<'UNIT'
[Unit]
Description=Telegram Promo Bot
After=network-online.target

[Service]
WorkingDirectory=/opt/bot_tg
ExecStart=/opt/bot_tg/.venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl enable --now promo-bot
```
