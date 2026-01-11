"""
指数行情相关 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models import get_db, IndexQuote
from ..scrapers import get_all_indices, INDEX_MAPPING

router = APIRouter(prefix="/indices", tags=["indices"])


@router.get("")
async def get_indices_realtime():
    """
    获取所有监控指数的实时行情
    """
    try:
        data = get_all_indices()

        # 添加中文名称
        for code, info in INDEX_MAPPING.items():
            if code in data:
                data[code]["display_name"] = info.get("name", code)

        return {
            "updated_at": datetime.now().isoformat(),
            "count": len(data),
            "data": data,
        }

    except Exception as e:
        return {"error": str(e), "data": {}}


@router.get("/{index_code}")
async def get_index_detail(
    index_code: str,
):
    """
    获取单个指数的详细行情
    """
    if index_code not in INDEX_MAPPING:
        return {"error": f"不支持的指数: {index_code}"}

    data = get_all_indices()
    if index_code in data:
        result = data[index_code]
        result["display_name"] = INDEX_MAPPING[index_code].get("name", index_code)
        return {
            "updated_at": datetime.now().isoformat(),
            "data": result,
        }

    return {"error": "获取数据失败"}


@router.get("/{index_code}/history")
async def get_index_history(
    index_code: str,
    days: int = Query(default=30, le=90, description="查询天数"),
    db: Session = Depends(get_db),
):
    """
    获取指数历史行情（从数据库）
    """
    since = datetime.utcnow() - timedelta(days=days)

    records = db.query(IndexQuote).filter(
        IndexQuote.index_code == index_code,
        IndexQuote.recorded_at >= since,
    ).order_by(IndexQuote.recorded_at.asc()).all()

    return {
        "index_code": index_code,
        "index_name": INDEX_MAPPING.get(index_code, {}).get("name", index_code),
        "days": days,
        "count": len(records),
        "data": [r.to_dict() for r in records],
    }


@router.get("/config/mapping")
async def get_index_mapping():
    """
    获取指数代码映射配置
    """
    result = {}
    for code, info in INDEX_MAPPING.items():
        result[code] = {
            "name": info.get("name", code),
            "sina_code": info.get("sina_code"),
            "yahoo_code": info.get("yahoo_code"),
        }
    return result
