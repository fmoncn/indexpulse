"""
QDII 溢价率相关 API 路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models import get_db, PremiumHistory
from ..scrapers import get_qdii_premium_data, TRACKED_FUNDS

router = APIRouter(prefix="/premium", tags=["premium"])


@router.get("")
async def get_current_premium(
    index_type: Optional[str] = Query(default=None, description="指数类型: sp500/nasdaq100/hsi/hstech"),
):
    """
    获取当前 QDII 溢价率数据（实时爬取）
    """
    try:
        data = get_qdii_premium_data()

        # 按指数类型过滤
        if index_type and index_type in TRACKED_FUNDS:
            target_codes = set(TRACKED_FUNDS[index_type])
            data = [d for d in data if d.get("fund_code") in target_codes]

        # 按指数类型分组
        grouped = {}
        for item in data:
            idx_type = item.get("index_type", "other")
            if idx_type not in grouped:
                grouped[idx_type] = []
            grouped[idx_type].append(item)

        return {
            "updated_at": datetime.now().isoformat(),
            "count": len(data),
            "data": data,
            "grouped": grouped,
        }

    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/history/{fund_code}")
async def get_premium_history(
    fund_code: str,
    days: int = Query(default=30, le=90, description="查询天数"),
    db: Session = Depends(get_db),
):
    """
    获取单只基金的溢价率历史
    """
    since = datetime.utcnow() - timedelta(days=days)

    records = db.query(PremiumHistory).filter(
        PremiumHistory.fund_code == fund_code,
        PremiumHistory.recorded_at >= since,
    ).order_by(PremiumHistory.recorded_at.asc()).all()

    return {
        "fund_code": fund_code,
        "days": days,
        "count": len(records),
        "data": [r.to_dict() for r in records],
    }


@router.get("/stats")
async def get_premium_stats(
    db: Session = Depends(get_db),
):
    """
    获取溢价率统计信息
    """
    # 获取最新数据
    current_data = get_qdii_premium_data()

    # 计算统计
    stats = {
        "total_funds": len(current_data),
        "high_premium": [],  # 高溢价
        "discount": [],      # 折价
    }

    for item in current_data:
        premium = item.get("premium_rate", 0)
        if premium > 1.5:
            stats["high_premium"].append({
                "fund_code": item.get("fund_code"),
                "fund_name": item.get("fund_name"),
                "premium_rate": premium,
            })
        elif premium < -1:
            stats["discount"].append({
                "fund_code": item.get("fund_code"),
                "fund_name": item.get("fund_name"),
                "premium_rate": premium,
            })

    # 按溢价率排序
    stats["high_premium"].sort(key=lambda x: x["premium_rate"], reverse=True)
    stats["discount"].sort(key=lambda x: x["premium_rate"])

    return stats


@router.get("/tracked-funds")
async def get_tracked_funds():
    """
    获取跟踪的基金列表
    """
    return {
        "funds": TRACKED_FUNDS,
        "description": {
            "sp500": "标普500指数",
            "nasdaq100": "纳斯达克100指数",
            "hsi": "恒生指数",
            "hstech": "恒生科技指数",
        }
    }
