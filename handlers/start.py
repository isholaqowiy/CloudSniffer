from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.future import select
from database.connection import AsyncSessionLocal
from database.models import User
from keyboards.inline import get_start_keyboard

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start_handler(message: Message, state: FSMContext):
    await state.clear()

    # Register user in DB if not already present
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        if not user:
            session.add(User(
                telegram_id=message.from_user.id,
                username=message.from_user.username
            ))
            await session.commit()

    first_name = message.from_user.first_name or "there"
    welcome_text = (
        f"👋 *Welcome, {first_name}!*\n\n"
        f"I'm your *AI Content Detector* — built to help academic instructors "
        f"perform digital forensic writing assessments on student assignments.\n\n"
        f"⚡ *How it works:*\n"
        f"I apply structural linguistic analysis combined with advanced processing "
        f"models to evaluate sentence complexity and predictability variations.\n\n"
        f"📌 *What you can do:*\n"
        f"• 🔍 Paste text directly for instant AI detection\n"
        f"• 📂 Upload `.pdf`, `.docx`, or `.txt` assignment files\n"
        f"• 📜 View your past detection history\n"
        f"• 💎 Upgrade to Premium for unlimited scans\n\n"
        f"Select an option below to get started 👇"
    )
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_start_keyboard()
    )

@start_router.callback_query(F.data == "action_help")
async def help_callback_handler(callback: CallbackQuery):
    help_text = (
        f"📖 *Documentation & Help*\n\n"
        f"• *Text Checking:* Paste any text directly into the chat.\n"
        f"• *Document Checking:* Upload `.pdf`, `.docx`, or `.txt` _(Premium only)_.\n"
        f"• *Minimum Length:* Input must be at least *100 characters*.\n"
        f"• *Daily Limit:* Free users get *5 scans per day*.\n\n"
        f"Use /start anytime to return to the main menu."
    )
    await callback.message.edit_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

@start_router.callback_query(F.data == "action_cancel")
async def cancel_action_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    first_name = callback.from_user.first_name or "there"
    await callback.message.edit_text(
        f"⚙️ Operation cancelled, {first_name}. Returning to main menu.",
        reply_markup=get_start_keyboard()
    )
    await callback.answer()
