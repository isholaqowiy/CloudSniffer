from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Detect AI Content", callback_data="action_detect")],
        [InlineKeyboardButton(text="📂 Upload Assignment File", callback_data="action_detect")],
        [InlineKeyboardButton(text="📜 History Log", callback_data="action_history")],
        [InlineKeyboardButton(text="💎 Premium Plans", callback_data="action_premium")],
        [InlineKeyboardButton(text="❓ Documentation Help", callback_data="action_help")]
    ])

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Abort Operation", callback_data="action_cancel")]
    ])

def get_export_keyboard(history_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 Export PDF", callback_data=f"export_pdf_{history_id}"),
            InlineKeyboardButton(text="📝 Export TXT", callback_data=f"export_txt_{history_id}")
        ]
    ])
