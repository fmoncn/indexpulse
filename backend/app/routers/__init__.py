"""
路由模块初始化
"""
from .events import router as events_router
from .premium import router as premium_router
from .fund_flow import router as fund_flow_router
from .indices import router as indices_router
from .prediction import router as prediction_router
from .market import router as market_router

__all__ = [
    "events_router",
    "premium_router",
    "fund_flow_router",
    "indices_router",
    "prediction_router",
    "market_router",
]
