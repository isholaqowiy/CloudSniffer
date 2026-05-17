from typing import Any, Awaitable, Callable, Dict
from datetime import date
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.future import select
from database.connection import AsyncSessionLocal
from database.models import User, DailyUsage

class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not event.text or not (event.text.startswith("/") or data.get("raw_state")):
            # If it's a structural command or outside standard state processing, skip checks.
            pass

        user_id = event.from_user.id
        async with AsyncSessionLocal() as session:
            # Synchronize active profile status or initialize defaults on-the-fly
            user_stmt = await session.execute(select(User).where(User.telegram_id == user_id))
            user = user_stmt.scalar_one_or_none()
            
            if not user:
                user = User(telegram_id=user_id, username=event.from_user.username)
                session.add(user)
                await session.commit()
                await session.refresh(user)

            data["user_profile"] = user
            
            # Explicit checking bypassing execution boundaries during functional steps
            state = data.get("state")
            current_state = await state.get_state() if state else None
            
            if current_state == "DetectionStates:WaitingForContent":
                if not user.is_premium:
                    today = date.today()
                    usage_stmt = await session.execute(
                        select(DailyUsage).where(DailyUsage.telegram_id == user_id, DailyUsage.usage_date == today)
                    )
                    usage = usage_stmt.scalar_one_or_none()
                    
                    if usage and usage.count >= 5:
                        return await event.answer(
                            "❌ *Daily Limit Reached (5/5)*\n\n"
                            "Free tier allocation exhausted. Please unlock Premium via /subscription to get unlimited access and document scans.",
                            parse_mode="Markdown"
                        )
        return await handler(event, data)
