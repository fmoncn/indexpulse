"""
市场指标爬虫
- VIX 恐慌指数
- 美元指数 DXY
- 美国国债收益率
- CNN Fear & Greed Index
"""
import logging
from typing import Dict, Optional
from datetime import datetime
from .base import BaseScraper

logger = logging.getLogger(__name__)


class MarketIndicatorsScraper(BaseScraper):
    """市场指标爬虫"""

    def get_vix(self) -> Optional[Dict]:
        """
        获取 VIX 恐慌指数 (通过 Yahoo Finance)
        """
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX"
        params = {"interval": "1d", "range": "5d"}

        try:
            data = self.get_json(url, params=params)
            if data is None:
                return None

            result = data.get("chart", {}).get("result", [])
            if not result:
                return None

            meta = result[0].get("meta", {})
            current = meta.get("regularMarketPrice", 0)
            previous_close = meta.get("previousClose", 0)
            change = current - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0

            # VIX 等级判断
            if current < 15:
                level = "low"
                sentiment = "贪婪"
            elif current < 20:
                level = "normal"
                sentiment = "平稳"
            elif current < 30:
                level = "elevated"
                sentiment = "谨慎"
            else:
                level = "high"
                sentiment = "恐慌"

            return {
                "value": round(current, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "previous_close": round(previous_close, 2),
                "level": level,
                "sentiment": sentiment,
                "updated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"获取 VIX 失败: {e}")
            return None

    def get_dxy(self) -> Optional[Dict]:
        """
        获取美元指数 DXY (通过 Yahoo Finance)
        """
        url = "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB"
        params = {"interval": "1d", "range": "5d"}

        try:
            data = self.get_json(url, params=params)
            if data is None:
                return None

            result = data.get("chart", {}).get("result", [])
            if not result:
                return None

            meta = result[0].get("meta", {})
            current = meta.get("regularMarketPrice", 0)
            previous_close = meta.get("previousClose", 0)
            change = current - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0

            # 美元强弱判断
            if current > 105:
                trend = "strong"
                description = "美元走强"
            elif current > 100:
                trend = "neutral"
                description = "美元平稳"
            else:
                trend = "weak"
                description = "美元走弱"

            return {
                "value": round(current, 3),
                "change": round(change, 3),
                "change_percent": round(change_percent, 2),
                "previous_close": round(previous_close, 3),
                "trend": trend,
                "description": description,
                "updated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"获取 DXY 失败: {e}")
            return None

    def get_treasury_yield(self, maturity: str = "10Y") -> Optional[Dict]:
        """
        获取美国国债收益率 (通过 Yahoo Finance)

        Args:
            maturity: 期限，支持 "2Y", "5Y", "10Y", "30Y"
        """
        symbols = {
            "2Y": "^IRX",      # 3个月国债 (用作短期)
            "5Y": "^FVX",      # 5年国债
            "10Y": "^TNX",     # 10年国债
            "30Y": "^TYX",     # 30年国债
        }

        symbol = symbols.get(maturity, "^TNX")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"interval": "1d", "range": "5d"}

        try:
            data = self.get_json(url, params=params)
            if data is None:
                return None

            result = data.get("chart", {}).get("result", [])
            if not result:
                return None

            meta = result[0].get("meta", {})
            # 收益率数据需要除以10（Yahoo格式）
            current = meta.get("regularMarketPrice", 0) / 10 if maturity != "2Y" else meta.get("regularMarketPrice", 0)
            previous_close = meta.get("previousClose", 0) / 10 if maturity != "2Y" else meta.get("previousClose", 0)
            change = current - previous_close

            return {
                "maturity": maturity,
                "yield": round(current, 3),
                "change": round(change, 3),
                "previous_close": round(previous_close, 3),
                "updated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"获取 {maturity} 国债收益率失败: {e}")
            return None

    def get_fear_greed_index(self) -> Optional[Dict]:
        """
        获取 CNN Fear & Greed Index
        通过东方财富获取类似的市场情绪指标
        """
        # 使用 A股 市场情绪作为替代
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "secid": "1.000001",  # 上证指数
            "fields": "f43,f44,f45,f46,f47,f169,f170,f171",
        }

        try:
            data = self.get_json(url, params=params)
            if data is None or not data.get("data"):
                return None

            d = data["data"]
            change_percent = d.get("f170", 0) / 100

            # 根据涨跌幅和成交量变化估算市场情绪
            # 简化版情绪计算
            if change_percent > 2:
                score = 80
                level = "extreme_greed"
                description = "极度贪婪"
            elif change_percent > 1:
                score = 65
                level = "greed"
                description = "贪婪"
            elif change_percent > 0:
                score = 55
                level = "neutral"
                description = "中性偏多"
            elif change_percent > -1:
                score = 45
                level = "neutral"
                description = "中性偏空"
            elif change_percent > -2:
                score = 35
                level = "fear"
                description = "恐惧"
            else:
                score = 20
                level = "extreme_fear"
                description = "极度恐惧"

            return {
                "score": score,
                "level": level,
                "description": description,
                "market_change": round(change_percent, 2),
                "updated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"获取市场情绪指标失败: {e}")
            return None


def get_all_market_indicators() -> Dict:
    """
    获取所有市场指标
    """
    with MarketIndicatorsScraper() as scraper:
        vix = scraper.get_vix()
        dxy = scraper.get_dxy()
        treasury_10y = scraper.get_treasury_yield("10Y")
        treasury_2y = scraper.get_treasury_yield("2Y")
        fear_greed = scraper.get_fear_greed_index()

        # 计算收益率曲线（10Y - 2Y）
        yield_curve = None
        if treasury_10y and treasury_2y:
            spread = treasury_10y["yield"] - treasury_2y["yield"]
            yield_curve = {
                "spread": round(spread, 3),
                "inverted": spread < 0,
                "description": "收益率曲线倒挂" if spread < 0 else "收益率曲线正常",
            }

        return {
            "vix": vix,
            "dxy": dxy,
            "treasury_10y": treasury_10y,
            "treasury_2y": treasury_2y,
            "yield_curve": yield_curve,
            "fear_greed": fear_greed,
            "updated_at": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    print("=== 市场指标 ===")
    indicators = get_all_market_indicators()

    if indicators.get("vix"):
        vix = indicators["vix"]
        print(f"VIX: {vix['value']} ({vix['change_percent']:+.2f}%) - {vix['sentiment']}")

    if indicators.get("dxy"):
        dxy = indicators["dxy"]
        print(f"DXY: {dxy['value']} ({dxy['change_percent']:+.2f}%) - {dxy['description']}")

    if indicators.get("treasury_10y"):
        t10 = indicators["treasury_10y"]
        print(f"10Y Treasury: {t10['yield']}%")

    if indicators.get("yield_curve"):
        yc = indicators["yield_curve"]
        print(f"Yield Curve Spread: {yc['spread']}% - {yc['description']}")

    if indicators.get("fear_greed"):
        fg = indicators["fear_greed"]
        print(f"Market Sentiment: {fg['score']} - {fg['description']}")
