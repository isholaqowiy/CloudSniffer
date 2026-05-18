import sys
import logging
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

# Configuration adjustments targeting absolute operational tracking visibility
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

# Register Global Middleware Infrastructure layers
dp.message.middleware(AntiSpamMiddleware())
dp.message.middleware(SubscriptionCheckMiddleware())

# Structural Routing Context Registrations
dp.include_router(start_router)
dp.include_router(detector_router)
dp.include_router(subscription_router)
dp.include_router(admin_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Initialization steps Sequence
    await init_db()
    webhook_target_url = f"{settings.WEBHOOK_URL}/webhook"
    logger.info(f"Setting physical telegram structural connection layer mappings towards: {webhook_target_url}")

    await bot.set_webhook(
        url=webhook_target_url,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )
    yield
    # Shutdown Processing parameters steps
    logger.info("De-allocating operational thread workers and removing global webhook states safely.")
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
        logger.error(f"Error encountered while feeding data pipeline update stream: {exc}")
        return Response(status_code=status.HTTP_200_OK)

@app.get("/health", status_code=status.HTTP_200_OK)
async def system_liveness_probe():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
