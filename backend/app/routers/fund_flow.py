"""
资金流向相关 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models import get_db, FundFlowHistory
from ..scrapers import get_north_flow, get_south_flow, EastMoneyScraper

router = APIRouter(prefix="/fund-flow", tags=["fund-flow"])


@router.get("/realtime")
async def get_realtime_flow():
    """
    获取实时资金流向（北向+南向）
    """
    north = get_north_flow()
    south = get_south_flow()

    return {
        "updated_at": datetime.now().isoformat(),
        "north": north,
        "south": south,
    }


@router.get("/north")
async def get_north_flow_data():
    """
    获取北向资金实时数据
    """
    data = get_north_flow()
    if data:
        return {
            "updated_at": datetime.now().isoformat(),
            "data": data,
        }
    return {"error": "获取数据失败", "data": None}


@router.get("/south")
async def get_south_flow_data():
    """
    获取南向资金实时数据
    """
    data = get_south_flow()
    if data:
        return {
            "updated_at": datetime.now().isoformat(),
            "data": data,
        }
    return {"error": "获取数据失败", "data": None}


@router.get("/north/history")
async def get_north_history(
    days: int = Query(default=20, le=60, description="查询天数"),
):
    """
    获取北向资金历史数据
    """
    with EastMoneyScraper() as scraper:
        data = scraper.fetch_north_flow_history(days=days)

    return {
        "days": days,
        "count": len(data),
        "data": data,
    }


@router.get("/history")
async def get_flow_history(
    flow_type: str = Query(default="north", description="资金类型: north/south"),
    days: int = Query(default=30, le=90, description="查询天数"),
    db: Session = Depends(get_db),
):
    """
    从数据库获取资金流向历史记录
    """
    since = datetime.utcnow() - timedelta(days=days)

    records = db.query(FundFlowHistory).filter(
        FundFlowHistory.flow_type == flow_type,
        FundFlowHistory.recorded_at >= since,
    ).order_by(FundFlowHistory.recorded_at.asc()).all()

    return {
        "flow_type": flow_type,
        "days": days,
        "count": len(records),
        "data": [r.to_dict() for r in records],
    }


@router.get("/stats")
async def get_flow_stats(
    db: Session = Depends(get_db),
):
    """
    获取资金流向统计
    """
    from sqlalchemy import func

    # 最近7天统计
    since_7d = datetime.utcnow() - timedelta(days=7)

    # 北向资金统计
    north_stats = db.query(
        func.sum(FundFlowHistory.total).label("total"),
        func.avg(FundFlowHistory.total).label("avg"),
        func.max(FundFlowHistory.total).label("max"),
        func.min(FundFlowHistory.total).label("min"),
    ).filter(
        FundFlowHistory.flow_type == "north",
        FundFlowHistory.recorded_at >= since_7d,
    ).first()

    # 南向资金统计
    south_stats = db.query(
        func.sum(FundFlowHistory.total).label("total"),
        func.avg(FundFlowHistory.total).label("avg"),
    ).filter(
        FundFlowHistory.flow_type == "south",
        FundFlowHistory.recorded_at >= since_7d,
    ).first()

    return {
        "period": "7d",
        "north": {
            "total": round(north_stats.total or 0, 2),
            "avg": round(north_stats.avg or 0, 2),
            "max": round(north_stats.max or 0, 2),
            "min": round(north_stats.min or 0, 2),
        } if north_stats else None,
        "south": {
            "total": round(south_stats.total or 0, 2),
            "avg": round(south_stats.avg or 0, 2),
        } if south_stats else None,
    }
