"""
指数行情爬虫
- 国内指数：新浪财经
- 美股指数：Yahoo Finance
- 港股指数：新浪财经
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
import re
from .base import BaseScraper

logger = logging.getLogger(__name__)


# 指数代码映射
INDEX_MAPPING = {
    # 国内指数 (新浪格式)
    "csi300": {"sina_code": "sh000300", "name": "沪深300"},
    "star50": {"sina_code": "sh000688", "name": "科创50"},
    # 港股指数 (新浪格式)
    "hsi": {"sina_code": "hkHSI", "name": "恒生指数"},
    "hstech": {"sina_code": "hkHSTECH", "name": "恒生科技"},
    # 美股指数 (Yahoo格式)
    "sp500": {"yahoo_code": "^GSPC", "name": "标普500"},
    "nasdaq100": {"yahoo_code": "^NDX", "name": "纳斯达克100"},
}


class SinaScraper(BaseScraper):
    """新浪财经行情爬虫"""

    QUOTE_URL = "https://hq.sinajs.cn/list="

    def __init__(self):
        super().__init__()
        self.session.headers.update({
            "Referer": "https://finance.sina.com.cn/",
        })

    def fetch_quotes(self, codes: List[str]) -> Dict[str, Dict]:
        """
        批量获取行情

        Args:
            codes: 新浪格式的代码列表，如 ["sh000300", "hkHSI"]

        Returns:
            行情数据字典
        """
        if not codes:
            return {}

        url = self.QUOTE_URL + ",".join(codes)

        try:
            response = self.get(url)
            if response is None:
                return {}

            # 设置正确的编码
            response.encoding = "gbk"
            text = response.text

            results = {}
            for code in codes:
                pattern = rf'var hq_str_{code}="([^"]*)"'
                match = re.search(pattern, text)
                if match:
                    data_str = match.group(1)
                    parsed = self._parse_quote(code, data_str)
                    if parsed:
                        results[code] = parsed

            return results

        except Exception as e:
            logger.error(f"获取新浪行情异常: {e}")
            return {}

    def _parse_quote(self, code: str, data_str: str) -> Optional[Dict]:
        """解析行情数据"""
        if not data_str:
            return None

        parts = data_str.split(",")

        try:
            # A股指数格式: 名称,今开,昨收,当前,最高,最低,买入,卖出,成交量,成交额,...
            if code.startswith("sh") or code.startswith("sz"):
                if len(parts) < 10:
                    return None
                name = parts[0]
                current = float(parts[3]) if parts[3] else 0
                yesterday_close = float(parts[2]) if parts[2] else 0
                change = current - yesterday_close
                change_percent = (change / yesterday_close * 100) if yesterday_close else 0

                return {
                    "name": name,
                    "price": current,
                    "change": change,
                    "change_percent": round(change_percent, 2),
                    "open": float(parts[1]) if parts[1] else 0,
                    "high": float(parts[4]) if parts[4] else 0,
                    "low": float(parts[5]) if parts[5] else 0,
                    "volume": float(parts[8]) if parts[8] else 0,
                    "amount": float(parts[9]) if parts[9] else 0,
                }

            # 港股格式: 名称,今开,昨收,最高,最低,当前,涨跌,涨幅%,买入,卖出,成交量,成交额,时间
            elif code.startswith("hk"):
                if len(parts) < 10:
                    return None
                name = parts[0]
                current = float(parts[6]) if parts[6] else 0
                yesterday_close = float(parts[3]) if parts[3] else 0
                change = float(parts[7]) if parts[7] else 0
                change_percent = float(parts[8]) if parts[8] else 0

                return {
                    "name": name,
                    "price": current,
                    "change": change,
                    "change_percent": change_percent,
                    "open": float(parts[2]) if parts[2] else 0,
                    "high": float(parts[4]) if parts[4] else 0,
                    "low": float(parts[5]) if parts[5] else 0,
                    "volume": float(parts[11]) if len(parts) > 11 and parts[11] else 0,
                }

        except (ValueError, IndexError) as e:
            logger.error(f"解析行情失败 {code}: {e}")

        return None


class YahooScraper(BaseScraper):
    """Yahoo Finance 行情爬虫（美股指数）"""

    QUOTE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"

    def fetch_quote(self, symbol: str) -> Optional[Dict]:
        """
        获取单个美股指数行情

        Args:
            symbol: Yahoo格式代码，如 "^GSPC"

        Returns:
            行情数据
        """
        url = f"{self.QUOTE_URL}{symbol}"
        params = {
            "interval": "1d",
            "range": "1d",
        }

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

            return {
                "name": meta.get("shortName", symbol),
                "price": current,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "open": meta.get("regularMarketOpen", 0),
                "high": meta.get("regularMarketDayHigh", 0),
                "low": meta.get("regularMarketDayLow", 0),
                "volume": meta.get("regularMarketVolume", 0),
                "market_state": meta.get("marketState", ""),  # PRE/REGULAR/POST/CLOSED
            }

        except Exception as e:
            logger.error(f"获取Yahoo行情异常 {symbol}: {e}")
            return None


def get_all_indices() -> Dict[str, Dict]:
    """
    获取所有监控指数的行情

    Returns:
        所有指数行情数据
    """
    results = {}

    # 获取国内和港股指数（新浪）
    sina_codes = []
    sina_to_index = {}
    for index_code, info in INDEX_MAPPING.items():
        if "sina_code" in info:
            sina_codes.append(info["sina_code"])
            sina_to_index[info["sina_code"]] = index_code

    with SinaScraper() as scraper:
        sina_data = scraper.fetch_quotes(sina_codes)
        for sina_code, quote in sina_data.items():
            index_code = sina_to_index.get(sina_code)
            if index_code:
                quote["index_code"] = index_code
                quote["recorded_at"] = datetime.now().isoformat()
                results[index_code] = quote

    # 获取美股指数（Yahoo）
    with YahooScraper() as scraper:
        for index_code, info in INDEX_MAPPING.items():
            if "yahoo_code" in info:
                quote = scraper.fetch_quote(info["yahoo_code"])
                if quote:
                    quote["index_code"] = index_code
                    quote["recorded_at"] = datetime.now().isoformat()
                    results[index_code] = quote

    logger.info(f"成功获取 {len(results)} 个指数行情")
    return results


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    print("=== 所有指数行情 ===")
    indices = get_all_indices()
    for code, data in indices.items():
        print(f"{code}: {data['name']} {data['price']:.2f} ({data['change_percent']:+.2f}%)")
