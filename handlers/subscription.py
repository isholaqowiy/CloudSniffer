from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from sqlalchemy.future import select
from database.connection import AsyncSessionLocal
from database.models import User

subscription_router = Router()

@subscription_router.message(Command("subscription"))
async def subscription_cmd_handler(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        status = "💎 PREMIUM ACTIVE" if (user and user.is_premium) else "🆓 FREE TIER ACTIVE"

    tier_msg = (
        f"💳 *Subscription Management Portal*\n\n"
        f"Your active billing tier: `{status}`\n\n"
        f"✨ *Premium Benefits:*\n"
        f"• Unlimited detection processing allocations\n"
        f"• Native PDF/DOCX file ingestion\n"
        f"• High-resolution forensic report exports"
    )
    await message.answer(tier_msg, parse_mode="Markdown")

@subscription_router.callback_query(F.data == "action_premium")
async def subscription_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = result.scalar_one_or_none()
        status = "💎 PREMIUM ACTIVE" if (user and user.is_premium) else "🆓 FREE TIER ACTIVE"

    tier_msg = (
        f"💳 *Subscription Management Portal*\n\n"
        f"Your active billing tier: `{status}`\n\n"
        f"✨ Upgrade to unlock full file analysis by typing /subscription."
    )
    await callback.message.edit_text(tier_msg, parse_mode="Markdown")
    await callback.answer()
