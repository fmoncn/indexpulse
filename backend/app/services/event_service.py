"""
事件生成服务 - 根据数据变化生成事件
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models import Event, PremiumHistory, FundFlowHistory, IndexQuote

logger = logging.getLogger(__name__)


# 预警阈值配置
ALERT_THRESHOLDS = {
    "premium_high": 1.5,      # 溢价率高于此值预警
    "premium_low": -1.5,      # 折价率低于此值预警
    "fund_flow_high": 50,     # 北向资金单日超过50亿预警
    "fund_flow_low": -50,     # 北向资金单日流出超过50亿预警
    "price_change": 2.0,      # 指数涨跌幅超过2%预警
}


class EventService:
    """事件服务"""

    def __init__(self, db: Session):
        self.db = db

    def check_premium_alerts(self, premium_data: List[Dict]) -> List[Event]:
        """
        检查溢价率并生成预警事件

        Args:
            premium_data: 溢价率数据列表

        Returns:
            生成的事件列表
        """
        events = []

        for data in premium_data:
            fund_code = data.get("fund_code", "")
            fund_name = data.get("fund_name", "")
            premium_rate = data.get("premium_rate", 0)
            index_type = data.get("index_type", "")

            # 保存历史记录
            history = PremiumHistory(
                fund_code=fund_code,
                fund_name=fund_name,
                price=data.get("price", 0),
                nav=data.get("nav", 0),
                nav_date=data.get("nav_date", ""),
                premium_rate=premium_rate,
                volume=data.get("volume", 0),
            )
            self.db.add(history)

            # 检查是否需要预警
            if premium_rate >= ALERT_THRESHOLDS["premium_high"]:
                event = self._create_premium_event(
                    data, "high",
                    f"溢价率 {premium_rate:.2f}% 偏高，注意风险"
                )
                events.append(event)
                self.db.add(event)

            elif premium_rate <= ALERT_THRESHOLDS["premium_low"]:
                event = self._create_premium_event(
                    data, "low",
                    f"折价率 {abs(premium_rate):.2f}%，可能存在套利机会"
                )
                events.append(event)
                self.db.add(event)

        self.db.commit()
        return events

    def _create_premium_event(self, data: Dict, alert_type: str, summary: str) -> Event:
        """创建溢价率预警事件"""
        fund_code = data.get("fund_code", "")
        fund_name = data.get("fund_name", "")
        premium_rate = data.get("premium_rate", 0)
        index_type = data.get("index_type", "")

        # 确定影响方向和重要性
        if alert_type == "high":
            impact = "negative"  # 高溢价对买入者不利
            importance = 4 if premium_rate > 3 else 3
        else:
            impact = "positive"  # 折价对买入者有利
            importance = 4 if premium_rate < -3 else 3

        return Event(
            event_type="premium_alert",
            target_index=index_type,
            title=f"【{fund_name}】溢价率预警 {premium_rate:+.2f}%",
            summary=summary,
            impact=impact,
            importance=importance,
            data={
                "fund_code": fund_code,
                "fund_name": fund_name,
                "premium_rate": premium_rate,
                "price": data.get("price"),
                "nav": data.get("nav"),
                "alert_type": alert_type,
            }
        )

    def check_fund_flow_alerts(self, north_data: Optional[Dict], south_data: Optional[Dict]) -> List[Event]:
        """
        检查资金流向并生成预警事件

        Args:
            north_data: 北向资金数据
            south_data: 南向资金数据

        Returns:
            生成的事件列表
        """
        events = []

        # 处理北向资金
        if north_data:
            total = north_data.get("total", 0)

            # 保存历史记录
            history = FundFlowHistory(
                flow_type="north",
                sh_connect=north_data.get("sh_connect", 0),
                sz_connect=north_data.get("sz_connect", 0),
                total=total,
            )
            self.db.add(history)

            # 检查是否需要预警
            if total >= ALERT_THRESHOLDS["fund_flow_high"]:
                event = Event(
                    event_type="fund_flow",
                    target_index="csi300",  # 北向资金主要影响A股
                    title=f"北向资金大幅流入 {total:.2f}亿",
                    summary=f"沪股通 {north_data.get('sh_connect', 0):.2f}亿，深股通 {north_data.get('sz_connect', 0):.2f}亿",
                    impact="positive",
                    importance=4 if total > 80 else 3,
                    data=north_data,
                )
                events.append(event)
                self.db.add(event)

            elif total <= ALERT_THRESHOLDS["fund_flow_low"]:
                event = Event(
                    event_type="fund_flow",
                    target_index="csi300",
                    title=f"北向资金大幅流出 {abs(total):.2f}亿",
                    summary=f"沪股通 {north_data.get('sh_connect', 0):.2f}亿，深股通 {north_data.get('sz_connect', 0):.2f}亿",
                    impact="negative",
                    importance=4 if total < -80 else 3,
                    data=north_data,
                )
                events.append(event)
                self.db.add(event)

        # 处理南向资金（类似逻辑）
        if south_data:
            total = south_data.get("total", 0)

            history = FundFlowHistory(
                flow_type="south",
                sh_connect=south_data.get("hk_sh", 0),
                sz_connect=south_data.get("hk_sz", 0),
                total=total,
            )
            self.db.add(history)

            if abs(total) >= ALERT_THRESHOLDS["fund_flow_high"]:
                impact = "positive" if total > 0 else "negative"
                event = Event(
                    event_type="fund_flow",
                    target_index="hsi",
                    title=f"南向资金{'流入' if total > 0 else '流出'} {abs(total):.2f}亿",
                    summary=f"港股通(沪) {south_data.get('hk_sh', 0):.2f}亿，港股通(深) {south_data.get('hk_sz', 0):.2f}亿",
                    impact=impact,
                    importance=3,
                    data=south_data,
                )
                events.append(event)
                self.db.add(event)

        self.db.commit()
        return events

    def check_index_alerts(self, indices_data: Dict[str, Dict]) -> List[Event]:
        """
        检查指数行情并生成预警事件

        Args:
            indices_data: 指数行情数据

        Returns:
            生成的事件列表
        """
        events = []

        for index_code, data in indices_data.items():
            # 保存行情快照
            quote = IndexQuote(
                index_code=index_code,
                index_name=data.get("name", ""),
                price=data.get("price", 0),
                change=data.get("change", 0),
                change_percent=data.get("change_percent", 0),
                volume=data.get("volume", 0),
            )
            self.db.add(quote)

            # 检查涨跌幅是否超过阈值
            change_percent = data.get("change_percent", 0)
            if abs(change_percent) >= ALERT_THRESHOLDS["price_change"]:
                direction = "上涨" if change_percent > 0 else "下跌"
                impact = "positive" if change_percent > 0 else "negative"

                event = Event(
                    event_type="index_move",
                    target_index=index_code,
                    title=f"【{data.get('name', index_code)}】{direction} {abs(change_percent):.2f}%",
                    summary=f"当前点位 {data.get('price', 0):.2f}，涨跌 {data.get('change', 0):+.2f}",
                    impact=impact,
                    importance=4 if abs(change_percent) > 3 else 3,
                    data=data,
                )
                events.append(event)
                self.db.add(event)

        self.db.commit()
        return events

    def get_recent_events(
        self,
        limit: int = 50,
        event_type: Optional[str] = None,
        target_index: Optional[str] = None,
        min_importance: int = 1,
    ) -> List[Event]:
        """
        获取最近的事件列表

        Args:
            limit: 返回数量限制
            event_type: 事件类型过滤
            target_index: 目标指数过滤
            min_importance: 最小重要性

        Returns:
            事件列表
        """
        query = self.db.query(Event).filter(Event.importance >= min_importance)

        if event_type:
            query = query.filter(Event.event_type == event_type)

        if target_index:
            query = query.filter(Event.target_index == target_index)

        return query.order_by(Event.created_at.desc()).limit(limit).all()
