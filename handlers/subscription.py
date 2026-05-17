from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from database.connection import AsyncSessionLocal
from database.models import User

subscription_router = Router()

@subscription_router.message(Command("subscription"))
async def subscription_cmd_handler(message: Message):
    async with AsyncSessionLocal() as session:
        res = await session.get(User, message.from_user.id)
        status = "💎 PREMIUM ACTIVE" if (res and res.is_premium) else "🆓 FREE TIER ACTIVE"
        
    tier_msg = (
        f"💳 *Subscription Management Portal*\n\n"
        f"Your active billing tier context: `{status}`\n\n"
        f"✨ *Premium Benefits:*\n"
        f"• Unlimited detection processing allocations.\n"
        f"• native ingestion processing for PDF/DOCX structures.\n"
        f"• High-resolution forensic generation export tools."
    )
    await message.answer(tier_msg, parse_mode="Markdown")

@subscription_router.callback_query(F.data == "action_premium")
async def subscription_callback_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        res = await session.get(User, callback.from_user.id)
        status = "💎 PREMIUM ACTIVE" if (res and res.is_premium) else "🆓 FREE TIER ACTIVE"
        
    tier_msg = (
        f"💳 *Subscription Management Portal*\n\n"
        f"Your active billing tier context: `{status}`\n\n"
        f"✨ Upgrade to unleash full file analysis integrations instantly by typing /subscription parameters."
    )
    await callback.message.edit_text(tier_msg, parse_mode="Markdown")
    await callback.answer()
