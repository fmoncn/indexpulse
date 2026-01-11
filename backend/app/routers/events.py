"""
事件相关 API 路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..models import get_db, Event
from ..services import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=None)
async def get_events(
    limit: int = Query(default=50, le=200, description="返回数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    event_type: Optional[str] = Query(default=None, description="事件类型: premium_alert/fund_flow/index_move"),
    target_index: Optional[str] = Query(default=None, description="目标指数: sp500/nasdaq100/csi300/star50/hsi"),
    min_importance: int = Query(default=1, ge=1, le=5, description="最小重要性"),
    db: Session = Depends(get_db),
):
    """
    获取事件列表

    支持按事件类型、目标指数、重要性过滤
    """
    query = db.query(Event).filter(Event.importance >= min_importance)

    if event_type:
        query = query.filter(Event.event_type == event_type)

    if target_index:
        query = query.filter(Event.target_index == target_index)

    total = query.count()
    events = query.order_by(Event.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": [event.to_dict() for event in events]
    }


@router.get("/{event_id}")
async def get_event_detail(
    event_id: int,
    db: Session = Depends(get_db),
):
    """获取单个事件详情"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {"error": "事件不存在"}
    return event.to_dict()


@router.get("/stats/summary")
async def get_event_stats(
    db: Session = Depends(get_db),
):
    """获取事件统计摘要"""
    from sqlalchemy import func
    from datetime import datetime, timedelta

    # 最近24小时
    since = datetime.utcnow() - timedelta(hours=24)

    # 按类型统计
    type_stats = db.query(
        Event.event_type,
        func.count(Event.id).label("count")
    ).filter(
        Event.created_at >= since
    ).group_by(Event.event_type).all()

    # 按指数统计
    index_stats = db.query(
        Event.target_index,
        func.count(Event.id).label("count")
    ).filter(
        Event.created_at >= since
    ).group_by(Event.target_index).all()

    return {
        "period": "24h",
        "by_type": {stat[0]: stat[1] for stat in type_stats if stat[0]},
        "by_index": {stat[0]: stat[1] for stat in index_stats if stat[0]},
    }
