import os
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

# 1. Setup logging to view issues in Render logs
logging.basicConfig(level=logging.INFO)

# 2. Initialize environment tokens
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Render provides the public URL via its blueprint or you can paste your service URL here
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://your-subdomain.onrender.com")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")

# 3. Initialize Bot and Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# --- TELEGRAM BOT HANDLERS ---

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    and triggers when a user presses the Start button.
    """
    # Custom Welcome Message
    welcome_text = (
        f"👋 *Welcome to Isacruzzbot, {message.from_user.full_name}!*\n\n"
        "I am up and running smoothly. Let me know how I can help you sniff out what you need today."
    )
    await message.answer(text=welcome_text, parse_mode=ParseMode.MARKDOWN)

# --- WEBHOOK ROUTING ---

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"

@app.on_event("startup")
async def on_startup():
    # Register the webhook URL with Telegram servers when FastAPI launches
    logging.info(f"Setting webhook to: {WEBHOOK_URL}")
    await bot.set_webhook(url=WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    # Receive updates forwarded by Telegram
    update = await request.json()
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

@app.on_event("shutdown")
async def on_shutdown():
    # Clean up connections on exit
    await bot.delete_webhook()
    await bot.session.close()

# --- RENDER PORT BINDING ---
if __name__ == "__main__":
    import uvicorn
    # Render binds internally to $PORT; fallback to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
