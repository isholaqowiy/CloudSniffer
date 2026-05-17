import asyncio
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.states import AdminStates
from database.connection import AsyncSessionLocal
from database.models import User, DetectionHistory, AdminNode
from sqlalchemy.future import select
from sqlalchemy import func

admin_router = Router()

async def verify_admin_status(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        stmt = await session.execute(select(AdminNode).where(AdminNode.telegram_id == user_id))
        return stmt.scalar_one_or_none() is not None

@admin_router.message(Command("admin"))
async def admin_dashboard_gateway(message: Message):
    # Fallback to bypass hard locks if DB verification nodes are uninitialized during bootstrap
    if not await verify_admin_status(message.from_user.id):
        # Programmatically seeding first administration scope node if configuration is fresh
        async with AsyncSessionLocal() as session:
            count_stmt = await session.execute(select(func.count(AdminNode.telegram_id)))
            if count_stmt.scalar() == 0:
                session.add(AdminNode(telegram_id=message.from_user.id))
                await session.commit()
            else:
                return await message.answer("🔒 *Restricted Boundary context:* Admin clearance not detected.")
                
    dashboard_text = (
        "⚡ *Administrator Management Nexus*\n\n"
        "/stats - View live usage metrics\n"
        "/users - List system user metrics\n"
        "/broadcast - Send an announcement to all users"
    )
    await message.answer(dashboard_text, parse_mode="Markdown")

@admin_router.message(Command("stats"))
async def admin_stats_handler(message: Message):
    if not await verify_admin_status(message.from_user.id):
        return
        
    async with AsyncSessionLocal() as session:
        users_count = (await session.execute(select(func.count(User.telegram_id)))).scalar()
        premium_count = (await session.execute(select(func.count(User.telegram_id)).where(User.is_premium == True))).scalar()
        detections_count = (await session.execute(select(func.count(DetectionHistory.id)))).scalar()
        
    stats_payload = (
        f"📊 *Global System Operational Matrix Metrics*\n\n"
        f"▪️ *Total Registered Instructors:* `{users_count}`\n"
        f"▪️ *Active Premium Allocations:* `{premium_count}`\n"
        f"▪️ *Total Forensic Tasks Handled:* `{detections_count}`"
    )
    await message.answer(stats_payload, parse_mode="Markdown")

@admin_router.message(Command("broadcast"))
async def admin_broadcast_init(message: Message, state: FSMContext):
    if not await verify_admin_status(message.from_user.id):
        return
    await state.set_state(AdminStates.WaitingForBroadcast)
    await message.answer("📢 Provide your target broadcast text content message context.")

@admin_router.message(AdminStates.WaitingForBroadcast)
async def admin_broadcast_execution_pipeline(message: Message, state: FSMContext, bot: Bot):
    if not await verify_admin_status(message.from_user.id):
        return
        
    broadcast_text = message.text
    await state.clear()
    
    async with AsyncSessionLocal() as session:
        users_stmt = await session.execute(select(User.telegram_id))
        user_ids = users_stmt.scalars().all()
        
    await message.answer(f"🚀 Processing async delivery tasks across `{len(user_ids)}` profiles.")
    
    delivered, failed = 0, 0
    for target_uid in user_ids:
        try:
            await bot.send_message(chat_id=target_uid, text=f"📢 *Notification Update From System Core:*\n\n{broadcast_text}", parse_mode="Markdown")
            delivered += 1
            await asyncio.sleep(0.05) # Concurrency rate-limiting logic on downstream workers
        except Exception:
            failed += 1
            
    await message.answer(f"🏁 *Broadcast Dispatch Complete.*\n\nDelivered: `{delivered}`\nFailed/Blocked: `{failed}`")
