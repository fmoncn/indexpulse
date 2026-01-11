"""
数据库模型定义
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库路径 - 使用绝对路径确保在任何目录下都能正常工作
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "indexpulse.db")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()


class Event(Base):
    """事件表 - 核心表，存储所有类型的事件"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False, index=True)  # premium_alert/fund_flow/macro/announcement
    target_index = Column(String(50), index=True)  # sp500/nasdaq100/csi300/star50/hsi
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    impact = Column(String(20))  # positive/negative/neutral
    importance = Column(Integer, default=3)  # 1-5星
    source_url = Column(String(500))
    data = Column(JSON)  # 扩展数据
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "target_index": self.target_index,
            "title": self.title,
            "summary": self.summary,
            "impact": self.impact,
            "importance": self.importance,
            "source_url": self.source_url,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PremiumHistory(Base):
    """QDII溢价率历史记录"""
    __tablename__ = "premium_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_code = Column(String(10), nullable=False, index=True)
    fund_name = Column(String(100))
    price = Column(Float)  # 场内价格
    nav = Column(Float)  # 净值
    nav_date = Column(String(20))  # 净值日期
    premium_rate = Column(Float)  # 溢价率 %
    volume = Column(Float)  # 成交额（万）
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "fund_code": self.fund_code,
            "fund_name": self.fund_name,
            "price": self.price,
            "nav": self.nav,
            "nav_date": self.nav_date,
            "premium_rate": self.premium_rate,
            "volume": self.volume,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None
        }


class FundFlowHistory(Base):
    """资金流向历史记录"""
    __tablename__ = "fund_flow_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flow_type = Column(String(20), nullable=False, index=True)  # north/south
    sh_connect = Column(Float)  # 沪股通净流入（亿）
    sz_connect = Column(Float)  # 深股通净流入（亿）
    total = Column(Float)  # 合计（亿）
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "flow_type": self.flow_type,
            "sh_connect": self.sh_connect,
            "sz_connect": self.sz_connect,
            "total": self.total,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None
        }


class IndexQuote(Base):
    """指数行情快照"""
    __tablename__ = "index_quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index_code = Column(String(20), nullable=False, index=True)  # sp500/nasdaq100/csi300/star50/hsi
    index_name = Column(String(50))
    price = Column(Float)  # 当前点位
    change = Column(Float)  # 涨跌点数
    change_percent = Column(Float)  # 涨跌幅 %
    volume = Column(Float)  # 成交量
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "index_code": self.index_code,
            "index_name": self.index_name,
            "price": self.price,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None
        }


class ETFInfo(Base):
    """ETF基础信息表"""
    __tablename__ = "etf_info"

    code = Column(String(10), primary_key=True)
    name = Column(String(100))
    index_type = Column(String(50))  # sp500/nasdaq100/csi300/star50/hsi
    fund_company = Column(String(100))
    is_qdii = Column(Boolean, default=False)
    track_index = Column(String(100))

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "index_type": self.index_type,
            "fund_company": self.fund_company,
            "is_qdii": self.is_qdii,
            "track_index": self.track_index
        }


class AlertConfig(Base):
    """预警配置表"""
    __tablename__ = "alert_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False)  # premium/fund_flow/price_change
    threshold = Column(Float)  # 阈值
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "threshold": self.threshold,
            "enabled": self.enabled
        }


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
