"""
东方财富 北向资金/南向资金 爬虫
数据来源：东方财富沪深港通资金流向
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
from .base import BaseScraper

logger = logging.getLogger(__name__)


class EastMoneyScraper(BaseScraper):
    """东方财富数据爬虫"""

    # 北向资金实时接口
    NORTH_FLOW_URL = "https://push2.eastmoney.com/api/qt/kamt.rtmin/get"

    # 北向资金历史接口
    NORTH_HISTORY_URL = "https://push2his.eastmoney.com/api/qt/kamt.kline/get"

    # 南向资金实时接口
    SOUTH_FLOW_URL = "https://push2.eastmoney.com/api/qt/kamtbs.rtmin/get"

    def __init__(self):
        super().__init__()
        self.session.headers.update({
            "Referer": "https://data.eastmoney.com/",
        })

    def fetch_north_flow_realtime(self) -> Optional[Dict]:
        """
        获取北向资金实时数据

        Returns:
            北向资金数据
        """
        params = {
            "fields1": "f1,f2,f3,f4",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "cb": "",
            "_": int(datetime.now().timestamp() * 1000),
        }

        try:
            data = self.get_json(self.NORTH_FLOW_URL, params=params)
            if data is None or "data" not in data:
                logger.error("获取北向资金数据失败")
                return None

            result = self._parse_north_flow(data["data"])
            logger.info(f"北向资金: 沪股通 {result['sh_connect']:.2f}亿, 深股通 {result['sz_connect']:.2f}亿")
            return result

        except Exception as e:
            logger.error(f"获取北向资金异常: {e}")
            return None

    def _parse_north_flow(self, data: Dict) -> Dict:
        """解析北向资金数据"""
        # 分钟级数据在 s2n 字段
        # 格式: "时间,沪股通净流入,深股通净流入,北向资金净流入,..."

        sh_connect = 0.0
        sz_connect = 0.0
        total = 0.0
        update_time = ""

        s2n = data.get("s2n", [])
        if s2n and len(s2n) > 0:
            # 获取最新一条数据
            latest = s2n[-1]
            parts = latest.split(",")
            if len(parts) >= 4:
                update_time = parts[0]
                # 数据单位是万，转换为亿
                sh_connect = self._safe_float(parts[1]) / 10000
                sz_connect = self._safe_float(parts[2]) / 10000
                total = self._safe_float(parts[3]) / 10000

        return {
            "flow_type": "north",
            "sh_connect": sh_connect,
            "sz_connect": sz_connect,
            "total": total,
            "update_time": update_time,
            "recorded_at": datetime.now().isoformat(),
        }

    def fetch_north_flow_history(self, days: int = 20) -> List[Dict]:
        """
        获取北向资金历史数据

        Args:
            days: 获取天数

        Returns:
            历史数据列表
        """
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",  # 日K
            "lmt": str(days),
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "_": int(datetime.now().timestamp() * 1000),
        }

        try:
            data = self.get_json(self.NORTH_HISTORY_URL, params=params)
            if data is None or "data" not in data:
                return []

            results = []
            s2n = data["data"].get("s2n", [])

            for item in s2n:
                parts = item.split(",")
                if len(parts) >= 4:
                    results.append({
                        "date": parts[0],
                        "sh_connect": self._safe_float(parts[1]) / 10000,  # 转换为亿
                        "sz_connect": self._safe_float(parts[2]) / 10000,
                        "total": self._safe_float(parts[3]) / 10000,
                    })

            return results

        except Exception as e:
            logger.error(f"获取北向资金历史异常: {e}")
            return []

    def fetch_south_flow_realtime(self) -> Optional[Dict]:
        """
        获取南向资金实时数据

        Returns:
            南向资金数据
        """
        params = {
            "fields1": "f1,f2,f3,f4",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "_": int(datetime.now().timestamp() * 1000),
        }

        try:
            data = self.get_json(self.SOUTH_FLOW_URL, params=params)
            if data is None or "data" not in data:
                logger.error("获取南向资金数据失败")
                return None

            result = self._parse_south_flow(data["data"])
            logger.info(f"南向资金: 港股通(沪) {result['hk_sh']:.2f}亿, 港股通(深) {result['hk_sz']:.2f}亿")
            return result

        except Exception as e:
            logger.error(f"获取南向资金异常: {e}")
            return None

    def _parse_south_flow(self, data: Dict) -> Dict:
        """解析南向资金数据"""
        hk_sh = 0.0
        hk_sz = 0.0
        total = 0.0
        update_time = ""

        n2s = data.get("n2s", [])
        if n2s and len(n2s) > 0:
            latest = n2s[-1]
            parts = latest.split(",")
            if len(parts) >= 4:
                update_time = parts[0]
                hk_sh = self._safe_float(parts[1]) / 10000
                hk_sz = self._safe_float(parts[2]) / 10000
                total = self._safe_float(parts[3]) / 10000

        return {
            "flow_type": "south",
            "hk_sh": hk_sh,  # 港股通(沪)
            "hk_sz": hk_sz,  # 港股通(深)
            "total": total,
            "update_time": update_time,
            "recorded_at": datetime.now().isoformat(),
        }

    def _safe_float(self, value, default: float = 0.0) -> float:
        """安全地转换为浮点数"""
        if value is None or value == "" or value == "-":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default


def get_north_flow() -> Optional[Dict]:
    """获取北向资金的便捷函数"""
    with EastMoneyScraper() as scraper:
        return scraper.fetch_north_flow_realtime()


def get_south_flow() -> Optional[Dict]:
    """获取南向资金的便捷函数"""
    with EastMoneyScraper() as scraper:
        return scraper.fetch_south_flow_realtime()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    print("=== 北向资金 ===")
    north = get_north_flow()
    if north:
        print(f"沪股通: {north['sh_connect']:.2f}亿")
        print(f"深股通: {north['sz_connect']:.2f}亿")
        print(f"合计: {north['total']:.2f}亿")

    print("\n=== 南向资金 ===")
    south = get_south_flow()
    if south:
        print(f"港股通(沪): {south['hk_sh']:.2f}亿")
        print(f"港股通(深): {south['hk_sz']:.2f}亿")
        print(f"合计: {south['total']:.2f}亿")
