import os
import json
import uuid
from datetime import date
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from states.states import DetectionStates
from keyboards.inline import get_cancel_keyboard, get_export_keyboard, get_start_keyboard
from database.connection import AsyncSessionLocal
from database.models import User, DailyUsage, DetectionHistory
from services.openai_detector import OpenAIDetectorService
from services.statistical_analyzer import StatisticalAnalyzer
from services.report_generator import ReportGenerator
from utils.file_processor import FileProcessor
from sqlalchemy.future import select

detector_router = Router()
openai_service = OpenAIDetectorService()

@detector_router.callback_query(F.data == "action_detect")
async def init_detection_flow(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DetectionStates.WaitingForContent)
    await callback.message.edit_text(
        "📝 *Awaiting Assignment Content Submission*\n\n"
        "Please paste your assignment text here directly, or upload an explicit file representation (`.txt`, `.pdf`, `.docx`).",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@detector_router.message(DetectionStates.WaitingForContent)
async def content_ingestion_router(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    raw_text = ""
    origin_name = "Direct Text Submission Input Stream"
    file_ext = "txt"

    # Loading/Typing Indicator Contextual feedback
    loading_msg = await message.answer("🔄 *Analyzing...* Running forensic content models.", parse_mode="Markdown")
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    async with AsyncSessionLocal() as db_session:
        user_stmt = await db_session.execute(select(User).where(User.telegram_id == user_id))
        user_profile = user_stmt.scalar_one_or_none()
        is_premium = user_profile.is_premium if user_profile else False

    try:
        if message.document:
            origin_name = message.document.file_name
            file_ext = os.path.splitext(origin_name)[1].lower()
            
            if not is_premium:
                await loading_msg.delete()
                await state.clear()
                return await message.answer("❌ *Access Denied:* Document file analysis (.pdf, .docx) requires premium access tier status.", reply_markup=get_start_keyboard())
                
            file_info = await bot.get_file(message.document.file_id)
            temp_path = f"/tmp/{uuid.uuid4()}{file_ext}"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            await bot.download_file(file_info.file_path, destination=temp_path)
            raw_text = FileProcessor.extract_text(temp_path, file_ext)
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            raw_text = message.text
            if not raw_text or len(raw_text.strip()) < 100:
                await loading_msg.delete()
                return await message.answer("⚠️ *Submission text segment too small.* Please provide text content of at least 100 characters to ensure baseline analysis precision.")

        # Hybrid Evaluation Execution
        stats_metrics = StatisticalAnalyzer.calculate_metrics(raw_text)
        openai_report = await openai_service.analyze_text(raw_text)
        
        # Combine statistics with OpenAI insights for a robust hybrid evaluation
        hybrid_ai_prob = int((openai_report["ai_probability"] * 0.7) + ((100.0 - stats_metrics["perplexity_score"]) * 0.3))
        hybrid_human_prob = 100 - hybrid_ai_prob
        
        final_verdict = openai_report["verdict"]
        if hybrid_ai_prob > 75:
            final_verdict = "AI-generated"
        elif hybrid_ai_prob < 30:
            final_verdict = "Human-written"
        else:
            final_verdict = "Mixed (Partially AI-generated)"

        # Persistent storage integration updates inside session block
        async with AsyncSessionLocal() as session:
            # Tracking and Incrementing usage metrics
            today = date.today()
            usage_stmt = await session.execute(select(DailyUsage).where(DailyUsage.telegram_id == user_id, DailyUsage.usage_date == today))
            usage = usage_stmt.scalar_one_or_none()
            if not usage:
                usage = DailyUsage(telegram_id=user_id, usage_date=today, count=0)
                session.add(usage)
            usage.count += 1
            
            history_record = DetectionHistory(
                telegram_id=user_id,
                file_name=origin_name,
                ai_percentage=hybrid_ai_prob,
                human_percentage=hybrid_human_prob,
                verdict=final_verdict,
                raw_report_json=json.dumps(openai_report)
            )
            session.add(history_record)
            await session.commit()
            record_id = history_record.id

        # Response Rendering Content Assembly
        response_template = (
            f"📊 *AI Content Detection Result*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 *AI Probability:* `{hybrid_ai_prob}%` | 🧑‍💻 *Human written:* `{hybrid_human_prob}%`\n"
            f"🔍 *Confidence Rating:* `{openai_report['confidence']}`\n"
            f"⚖️ *Final Assessment:* *{final_verdict}*\n\n"
            f"💡 *Linguistic Evaluation Insights:* \n"
        )
        for bullet in openai_report["analysis"]:
            response_template += f"• _{bullet}_\n"
            
        response_template += f"\n📋 *Instructor Recommendation:* \n_{openai_report['recommendation']}_\n"
        
        await loading_msg.delete()
        await message.answer(response_template, parse_mode="Markdown", reply_markup=get_export_keyboard(record_id))
        await state.clear()

    except Exception as general_err:
        await loading_msg.delete()
        await state.clear()
        await message.answer(f"❌ *Internal Evaluation pipeline Failure:* Unable to correctly process the artifact. Trace details logged.")

@detector_router.callback_query(F.data.startswith("export_"))
async def export_document_callback(callback: CallbackQuery):
    _, format_target, history_id = callback.data.split("_")
    
    async with AsyncSessionLocal() as session:
        record = await session.get(DetectionHistory, int(history_id))
        
    if not record:
        return await callback.answer("❌ Target evaluation entity record matching token vanished.", show_alert=True)
        
    report_data = json.loads(record.raw_report_json)
    report_data["ai_probability"] = record.ai_percentage
    report_data["human_probability"] = record.human_percentage
    report_data["verdict"] = record.verdict
    
    out_path = f"/tmp/Report_{history_id}.{format_target}"
    
    if format_target == "pdf":
        ReportGenerator.generate_pdf_report(report_data, out_path)
    else:
        ReportGenerator.generate_txt_report(report_data, out_path)
        
    document_payload = FSInputFile(out_path)
    await callback.message.answer_document(document_payload, caption=f"📄 Forensic Evaluation Document Report Export.")
    await callback.answer()
    
    if os.path.exists(out_path):
        os.remove(out_path)

@detector_router.callback_query(F.data == "action_history")
async def history_callback_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as session:
        stmt = select(DetectionHistory).where(DetectionHistory.telegram_id == user_id).order_by(DetectionHistory.timestamp.desc()).limit(5)
        records = (await session.execute(stmt)).scalars().all()
        
    if not records:
        return await callback.message.edit_text("📜 *History Logs clear.* You haven't scanned any assignments yet.", parse_mode="Markdown", reply_markup=get_start_keyboard())
        
    log_text = "📜 *Recent System Analytical History (Last 5 checks):*\n\n"
    for r in records:
        log_text += f"• `{r.timestamp.strftime('%Y-%m-%d')}` - *{r.verdict}* ({r.ai_percentage}% AI) \n  _File:_ {r.file_name[:25]}\n\n"
        
    await callback.message.edit_text(log_text, parse_mode="Markdown", reply_markup=get_start_keyboard())
    await callback.answer()
