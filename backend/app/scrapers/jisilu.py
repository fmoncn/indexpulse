"""
集思录 QDII 溢价率爬虫
数据来源：https://www.jisilu.cn/data/qdii/
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from .base import BaseScraper

logger = logging.getLogger(__name__)


# 我们关注的指数对应的QDII基金代码
TRACKED_FUNDS = {
    # 标普500
    "sp500": ["513500", "159612", "513650", "513850"],
    # 纳斯达克100
    "nasdaq100": ["513100", "159941", "513300", "159632"],
    # 恒生指数
    "hsi": ["159920", "513660", "513030"],
    # 恒生科技
    "hstech": ["513180", "513130", "159740"],
}

# 所有跟踪的基金代码集合
ALL_TRACKED_CODES = set()
for codes in TRACKED_FUNDS.values():
    ALL_TRACKED_CODES.update(codes)


class JisiluScraper(BaseScraper):
    """集思录 QDII 数据爬虫"""

    # QDII 数据接口
    QDII_API_URL = "https://www.jisilu.cn/data/qdii/qdii_list/"

    def __init__(self):
        super().__init__()
        # 集思录需要额外的请求头
        self.session.headers.update({
            "Referer": "https://www.jisilu.cn/data/qdii/",
            "X-Requested-With": "XMLHttpRequest",
        })

    def fetch_qdii_premium(self) -> List[Dict]:
        """
        获取所有QDII基金的溢价率数据

        Returns:
            包含溢价率数据的列表
        """
        try:
            # 构造请求参数
            params = {
                "___jsl": f"LST___t={int(datetime.now().timestamp() * 1000)}",
                "rp": "25",
                "page": "1",
            }

            response = self.get(self.QDII_API_URL, params=params)
            if response is None:
                logger.error("获取集思录QDII数据失败")
                return []

            # 尝试解析JSON
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"解析集思录响应失败: {e}")
                return []

            if "rows" not in data:
                logger.warning("集思录响应中没有rows字段")
                return []

            results = []
            for row in data["rows"]:
                cell = row.get("cell", {})
                fund_code = cell.get("fund_id", "")

                # 只保留我们关注的基金
                if fund_code not in ALL_TRACKED_CODES:
                    continue

                # 解析数据
                try:
                    premium_data = self._parse_fund_data(cell)
                    if premium_data:
                        results.append(premium_data)
                except Exception as e:
                    logger.error(f"解析基金 {fund_code} 数据失败: {e}")
                    continue

            logger.info(f"成功获取 {len(results)} 只QDII基金溢价率数据")
            return results

        except Exception as e:
            logger.error(f"获取QDII溢价率异常: {e}")
            return []

    def _parse_fund_data(self, cell: Dict) -> Optional[Dict]:
        """
        解析单个基金数据

        Args:
            cell: 原始数据

        Returns:
            格式化后的数据
        """
        fund_code = cell.get("fund_id", "")
        if not fund_code:
            return None

        # 确定基金对应的指数类型
        index_type = None
        for idx_type, codes in TRACKED_FUNDS.items():
            if fund_code in codes:
                index_type = idx_type
                break

        # 安全地解析数值
        def safe_float(value, default=0.0):
            if value is None or value == "" or value == "-":
                return default
            try:
                # 处理百分比格式
                if isinstance(value, str) and "%" in value:
                    return float(value.replace("%", ""))
                return float(value)
            except (ValueError, TypeError):
                return default

        # 获取溢价率（关键字段）
        premium_rt = safe_float(cell.get("premium_rt"))

        # 获取价格和净值
        price = safe_float(cell.get("price"))
        nav = safe_float(cell.get("nav"))

        # 获取估算净值（如果有）
        estimate_nav = safe_float(cell.get("estimate_nav"))
        if estimate_nav > 0:
            nav = estimate_nav

        return {
            "fund_code": fund_code,
            "fund_name": cell.get("fund_nm", ""),
            "index_type": index_type,
            "price": price,
            "nav": nav,
            "nav_date": cell.get("nav_dt", ""),
            "premium_rate": premium_rt,
            "volume": safe_float(cell.get("volume")),  # 成交额（万）
            "increase_rt": safe_float(cell.get("increase_rt")),  # 涨跌幅
            "apply_status": cell.get("apply_st", ""),  # 申购状态
            "redeem_status": cell.get("redeem_st", ""),  # 赎回状态
            "recorded_at": datetime.now().isoformat(),
        }

    def fetch_fund_detail(self, fund_code: str) -> Optional[Dict]:
        """
        获取单个基金的详细信息（备用方法）

        Args:
            fund_code: 基金代码

        Returns:
            基金详情
        """
        url = f"https://www.jisilu.cn/data/qdii/detail/{fund_code}"
        response = self.get(url)
        if response is None:
            return None

        try:
            return response.json()
        except Exception as e:
            logger.error(f"解析基金详情失败: {e}")
            return None


def get_qdii_premium_data() -> List[Dict]:
    """
    获取QDII溢价率数据的便捷函数

    Returns:
        溢价率数据列表
    """
    with JisiluScraper() as scraper:
        return scraper.fetch_qdii_premium()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    data = get_qdii_premium_data()
    for item in data:
        print(f"{item['fund_code']} {item['fund_name']}: 溢价率 {item['premium_rate']:.2f}%")
