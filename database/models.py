from datetime import datetime, date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, Text, Integer, ForeignKey, Date, DateTime, Boolean

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class DetectionHistory(Base):
    __tablename__ = "detection_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    file_name: Mapped[str] = mapped_column(String(255), default="Plain Text Direct Submission")
    ai_percentage: Mapped[int] = mapped_column(Integer)
    human_percentage: Mapped[int] = mapped_column(Integer)
    verdict: Mapped[str] = mapped_column(String(50))
    raw_report_json: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class DailyUsage(Base):
    __tablename__ = "daily_usage"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    usage_date: Mapped[date] = mapped_column(Date, default=date.today)
    count: Mapped[int] = mapped_column(Integer, default=0)

class AdminNode(Base):
    __tablename__ = "admin_nodes"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
