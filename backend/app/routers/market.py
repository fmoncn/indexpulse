"""
市场指标 API 路由
- VIX 恐慌指数
- 美元指数 DXY
- 美国国债收益率
- 市场情绪指标
"""
from fastapi import APIRouter
from datetime import datetime

from ..scrapers import get_all_market_indicators

router = APIRouter(prefix="/market", tags=["market"])


@router.get("")
async def get_market_indicators():
    """
    获取所有市场指标
    """
    try:
        data = get_all_market_indicators()
        return {
            "updated_at": datetime.now().isoformat(),
            "data": data,
        }
    except Exception as e:
        return {"error": str(e), "data": {}}


@router.get("/vix")
async def get_vix():
    """
    获取 VIX 恐慌指数
    """
    try:
        data = get_all_market_indicators()
        return {
            "updated_at": datetime.now().isoformat(),
            "data": data.get("vix"),
        }
    except Exception as e:
        return {"error": str(e), "data": None}


@router.get("/dxy")
async def get_dxy():
    """
    获取美元指数 DXY
    """
    try:
        data = get_all_market_indicators()
        return {
            "updated_at": datetime.now().isoformat(),
            "data": data.get("dxy"),
        }
    except Exception as e:
        return {"error": str(e), "data": None}


@router.get("/treasury")
async def get_treasury():
    """
    获取美国国债收益率
    """
    try:
        data = get_all_market_indicators()
        return {
            "updated_at": datetime.now().isoformat(),
            "data": {
                "10y": data.get("treasury_10y"),
                "2y": data.get("treasury_2y"),
                "yield_curve": data.get("yield_curve"),
            },
        }
    except Exception as e:
        return {"error": str(e), "data": None}


@router.get("/sentiment")
async def get_sentiment():
    """
    获取市场情绪指标
    """
    try:
        data = get_all_market_indicators()
        return {
            "updated_at": datetime.now().isoformat(),
            "data": data.get("fear_greed"),
        }
    except Exception as e:
        return {"error": str(e), "data": None}
