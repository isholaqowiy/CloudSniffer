import logging
from typing import Any, Awaitable, Callable, Dict
from datetime import date
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.future import select
from database.connection import AsyncSessionLocal
from database.models import User, DailyUsage

logger = logging.getLogger("SubscriptionMiddleware")

EXEMPT_COMMANDS = {
    "/start", "/help", "/subscription",
    "/cancel", "/admin", "/stats", "/broadcast"
}

class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        try:
            # Always pass through exempt commands
            if event.text and event.text.split()[0].lower().split("@")[0] in EXEMPT_COMMANDS:
                return await handler(event, data)

            user_id = event.from_user.id

            async with AsyncSessionLocal() as session:
                try:
                    user_stmt = await session.execute(
                        select(User).where(User.telegram_id == user_id)
                    )
                    user = user_stmt.scalar_one_or_none()

                    if not user:
                        user = User(
                            telegram_id=user_id,
                            username=event.from_user.username
                        )
                        session.add(user)
                        await session.commit()
                        await session.refresh(user)

                    data["user_profile"] = user

                    state = data.get("state")
                    current_state = await state.get_state() if state else None

                    if current_state == "DetectionStates:WaitingForContent":
                        if not user.is_premium:
                            today = date.today()
                            usage_stmt = await session.execute(
                                select(DailyUsage).where(
                                    DailyUsage.telegram_id == user_id,
                                    DailyUsage.usage_date == today
                                )
                            )
                            usage = usage_stmt.scalar_one_or_none()
                            if usage and usage.count >= 5:
                                return await event.answer(
                                    "❌ *Daily Limit Reached (5/5)*\n\n"
                                    "Free tier exhausted. Use /subscription to upgrade.",
                                    parse_mode="Markdown"
                                )
                except Exception as db_err:
                    logger.error(f"DB error in middleware for user {event.from_user.id}: {db_err}")
                    # Do not block the handler even if DB fails
                    pass

        except Exception as outer_err:
            logger.error(f"Outer middleware error: {outer_err}")

        return await handler(event, data)
