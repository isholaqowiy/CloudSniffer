from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_start_keyboard

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start_handler(message: Message, state: FSMContext):
    await state.clear()
    welcome_text = (
        f"👋 *Welcome to the AI Content Detector for Teachers!*\n\n"
        f"This application is tailored to assist academic instructors in performing digital "
        f"forensic writing assessments on student assignments.\n\n"
        f"⚡ *How it works:*\n"
        f"We apply structural linguistic analysis combined with advanced processing models to evaluate sentence complexity and predictability variations.\n\n"
        f"Select an execution option below to initiate processing."
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_start_keyboard())

@start_router.callback_query(F.data == "action_help")
async def help_callback_handler(callback: CallbackQuery):
    help_text = (
        f"📖 *System Documentation & Help*\n\n"
        f"• *Text Checking:* Send copy-pasted textual passages directly to the engine.\n"
        f"• *Document Checking:* Premium users can upload `.pdf`, `.docx`, or `.txt` directly.\n"
        f"• *Linguistic Bounds:* For reliable detection accuracy, keep input data lengths above 150 characters."
    )
    await callback.message.edit_text(help_text, parse_mode="Markdown", reply_markup=get_start_keyboard())
    await callback.answer()

@start_router.callback_query(F.data == "action_cancel")
async def cancel_action_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("⚙️ Active task cancelled. Main interface re-initialized.", reply_markup=get_start_keyboard())
    await callback.answer()
