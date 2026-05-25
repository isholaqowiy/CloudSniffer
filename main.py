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


async def keep_alive_loop():
    """
    Pings /health every 2 minutes to prevent Render free tier
    from spinning down the service due to inactivity.
    """
    await asyncio.sleep(60)  # Wait 1 minute after startup before first ping
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"{settings.WEBHOOK_URL}/health"
                response = await client.get(url)
                logger.info(f"Keep-alive ping → {url} — HTTP {response.status_code}")
        except Exception as e:
            logger.warning(f"Keep-alive ping failed (non-critical): {e}")
        await asyncio.sleep(120)  # Ping every 2 minutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    await init_db()

    if not settings.WEBHOOK_URL or not settings.WEBHOOK_URL.startswith("https://"):
        raise ValueError(
            f"WEBHOOK_URL is invalid: '{settings.WEBHOOK_URL}'. "
            f"Must be full HTTPS URL e.g. https://your-app.onrender.com"
        )

    webhook_url = f"{settings.WEBHOOK_URL}/webhook"
    logger.info(f"Registering webhook: {webhook_url}")

    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )
    logger.info("Webhook registered successfully.")

    keep_alive_task = asyncio.create_task(keep_alive_loop())
    logger.info("Keep-alive background task started.")

    yield

    # ── Shutdown ─────────────────────────────────────────────
    keep_alive_task.cancel()
    try:
        await keep_alive_task
    except asyncio.CancelledError:
        pass

    logger.info("Shutting down — removing webhook and closing session.")
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
        logger.error(f"Webhook processing error: {exc}")
        return Response(status_code=status.HTTP_200_OK)


@app.get("/health", status_code=status.HTTP_200_OK)
async def system_liveness_probe():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"status": "running"}
