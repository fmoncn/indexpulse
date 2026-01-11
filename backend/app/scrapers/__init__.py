"""
爬虫模块初始化
"""
from .base import BaseScraper
from .jisilu import JisiluScraper, get_qdii_premium_data, TRACKED_FUNDS
from .eastmoney import EastMoneyScraper, get_north_flow, get_south_flow
from .indices import SinaScraper, YahooScraper, get_all_indices, INDEX_MAPPING
from .market_indicators import MarketIndicatorsScraper, get_all_market_indicators

__all__ = [
    "BaseScraper",
    "JisiluScraper",
    "get_qdii_premium_data",
    "TRACKED_FUNDS",
    "EastMoneyScraper",
    "get_north_flow",
    "get_south_flow",
    "SinaScraper",
    "YahooScraper",
    "get_all_indices",
    "INDEX_MAPPING",
    "MarketIndicatorsScraper",
    "get_all_market_indicators",
]
