from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_start_keyboard

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start_handler(message: Message, state: FSMContext):
    await state.clear()
    first_name = message.from_user.first_name or "there"
    welcome_text = (
        f"👋 *Welcome, {first_name}!*\n\n"
        f"I'm your *AI Content Detector* — built to help academic instructors perform "
        f"digital forensic writing assessments on student assignments.\n\n"
        f"⚡ *How it works:*\n"
        f"I apply structural linguistic analysis combined with advanced processing models "
        f"to evaluate sentence complexity and predictability variations.\n\n"
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
        f"• *Document Checking:* Upload `.pdf`, `.docx`, or `.txt` files _(Premium only)_.\n"
        f"• *Minimum Length:* For reliable accuracy, input must be at least *150 characters*.\n"
        f"• *Daily Limit:* Free users get *5 scans per day*. Upgrade for unlimited access.\n\n"
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
