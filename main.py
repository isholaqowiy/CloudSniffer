import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

# 1. Setup logging to view issues in Render logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Initialize environment tokens
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Render automatically sets RENDER_EXTERNAL_URL if you enable it in settings
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://cloudsniffer.onrender.com")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")

# 3. Initialize Bot and Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- LIFESPAN MANAGER (Replaces deprecated @app.on_event) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block executes BEFORE the server starts accepting requests
    webhook_path = f"/webhook/{TOKEN}"
    webhook_url = f"{RENDER_EXTERNAL_URL}{webhook_path}"
    
    logger.info(f"Connecting to Telegram... Setting webhook to: {webhook_url}")
    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    
    yield  # The application runs while suspended here
    
    # This block executes when the server is shutting down
    logger.info("Server shutting down. Removing webhook configurations...")
    await bot.delete_webhook()
    await bot.session.close()

# 4. Pass the lifespan context directly into FastAPI initialization
app = FastAPI(lifespan=lifespan)

# --- TELEGRAM BOT HANDLERS ---

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    Triggers instantly when a user clicks the "Start" button or types /start.
    """
    welcome_text = (
        f"👋 *Welcome to CloudSniffer, {message.from_user.full_name}!*\n\n"
        "I am up and running smoothly on Render. Let me know how I can help you sniff out what you need today."
    )
    await message.answer(text=welcome_text, parse_mode=ParseMode.MARKDOWN)

# --- WEBHOOK ROUTING ---

@app.post(f"/webhook/{TOKEN}")
async def bot_webhook(request: Request):
    try:
        update_data = await request.json()
        telegram_update = types.Update(**update_data)
        await dp.feed_update(bot, telegram_update)
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}", exc_info=True)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- RENDER PORT BINDING ---
if __name__ == "__main__":
    import uvicorn
    # Render binds internally to $PORT environment hook; fallback to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
