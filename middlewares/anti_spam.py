import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

EXEMPT_COMMANDS = {"/start", "/help", "/subscription", "/admin", "/stats", "/broadcast"}

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit_seconds: int = 3):
        self.limit = limit_seconds
        self.storage = {}
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Never spam-block exempt commands
        if event.text and event.text.split()[0].lower().split("@")[0] in EXEMPT_COMMANDS:
            return await handler(event, data)

        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.storage:
            last_time = self.storage[user_id]
            if current_time - last_time < self.limit:
                return await event.answer(
                    "⚠️ *Slow down!* Please avoid spamming requests.",
                    parse_mode="Markdown"
                )

        self.storage[user_id] = current_time
        return await handler(event, data)
