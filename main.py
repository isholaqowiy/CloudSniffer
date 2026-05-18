import sys
import asyncio
import logging
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from config.config import settings
from database.connection import init_db
from middlewares.anti_spam import AntiSpamMiddleware
from middlewares.subscription_check import SubscriptionCheckMiddleware
from handlers.start import start_router
from handlers.detector import detector_router
from handlers.subscription import subscription_router
from handlers.admin import admin_router
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("ApplicationRuntimeEngine")

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(AntiSpamMiddleware())
dp.message.middleware(SubscriptionCheckMiddleware())

dp.include_router(start_router)
dp.include_router(detector_router)
dp.include_router(subscription_router)
dp.include_router(admin_router)

async def keep_alive():
    """Pings the service every 10 minutes to prevent Render free tier spin-down."""
    url = f"{settings.WEBHOOK_URL}/health"
    while True:
        await asyncio.sleep(600)  # every 10 minutes
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10)
                logger.info(f"Keep-alive ping sent → status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Keep-alive ping failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    if not settings.WEBHOOK_URL or not settings.WEBHOOK_URL.startswith("https://"):
        raise ValueError(
            f"WEBHOOK_URL is invalid or not set: '{settings.WEBHOOK_URL}'. "
            "Must be a full HTTPS URL e.g. https://your-app.onrender.com"
        )

    webhook_target_url = f"{settings.WEBHOOK_URL}/webhook"
    logger.info(f"Setting webhook towards: {webhook_target_url}")

    await bot.set_webhook(
        url=webhook_target_url,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )

    # Start keep-alive background task
    task = asyncio.create_task(keep_alive())
    logger.info("Keep-alive background task started.")

    yield

    task.cancel()
    logger.info("Removing webhook and closing session.")
    await bot.delete_webhook()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram_webhook_endpoint(request: Request):
    try:
        payload = await request.json()
        tg_update = Update.model_validate(payload, context={"bot": bot})
        await dp.feed_update(bot, tg_update)
        return Response(status_code=status.HTTP_200_OK)
    except Exception as exc:
        logger.error(f"Error processing update: {exc}")
        return Response(status_code=status.HTTP_200_OK)

@app.get("/health", status_code=status.HTTP_200_OK)
async def system_liveness_probe():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
