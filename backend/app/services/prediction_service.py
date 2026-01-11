"""
48小时指数预测服务
基于多维度数据综合分析生成预测
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from ..models import IndexPrediction, IndexQuote, FundFlowHistory, PremiumHistory
from ..scrapers import get_all_indices, INDEX_MAPPING, get_all_market_indicators

logger = logging.getLogger(__name__)


class PredictionService:
    """指数预测服务"""

    def __init__(self, db: Session):
        self.db = db

    def generate_predictions(self) -> List[Dict]:
        """
        生成所有指数的48小时预测
        综合考虑：
        1. 近期价格趋势
        2. 资金流向（北向资金）
        3. QDII溢价率
        4. 技术指标
        5. VIX恐慌指数
        6. 美元指数
        7. 美债收益率
        """
        predictions = []

        # 获取当前行情
        current_quotes = get_all_indices()

        # 获取市场指标
        self.market_indicators = get_all_market_indicators()

        for index_code, info in INDEX_MAPPING.items():
            try:
                prediction = self._generate_single_prediction(
                    index_code,
                    info.get("name", index_code),
                    current_quotes.get(index_code)
                )
                if prediction:
                    predictions.append(prediction)
            except Exception as e:
                logger.error(f"生成 {index_code} 预测失败: {e}")

        return predictions

    def _generate_single_prediction(
        self,
        index_code: str,
        index_name: str,
        current_quote: Optional[Dict]
    ) -> Optional[Dict]:
        """生成单个指数的预测"""

        factors = []
        score = 0  # 综合评分 (-100 到 100)

        current_price = current_quote.get("price", 0) if current_quote else 0

        # 因素1: 近期价格趋势
        trend_score, trend_factor = self._analyze_price_trend(index_code)
        score += trend_score * 0.3
        if trend_factor:
            factors.append(trend_factor)

        # 因素2: 资金流向 (主要影响A股指数)
        if index_code in ["csi300", "star50"]:
            flow_score, flow_factor = self._analyze_fund_flow()
            score += flow_score * 0.25
            if flow_factor:
                factors.append(flow_factor)

        # 因素3: QDII溢价率 (反映市场情绪)
        premium_score, premium_factor = self._analyze_premium(index_code)
        score += premium_score * 0.2
        if premium_factor:
            factors.append(premium_factor)

        # 因素4: 当日涨跌幅动量
        if current_quote:
            momentum_score, momentum_factor = self._analyze_momentum(current_quote)
            score += momentum_score * 0.15
            if momentum_factor:
                factors.append(momentum_factor)

        # 因素5: VIX恐慌指数 (主要影响美股)
        if index_code in ["sp500", "nasdaq100"]:
            vix_score, vix_factor = self._analyze_vix()
            score += vix_score * 0.15
            if vix_factor:
                factors.append(vix_factor)

        # 因素6: 美元指数 (影响全球市场)
        dxy_score, dxy_factor = self._analyze_dxy(index_code)
        score += dxy_score * 0.1
        if dxy_factor:
            factors.append(dxy_factor)

        # 因素7: 美债收益率
        if index_code in ["sp500", "nasdaq100"]:
            yield_score, yield_factor = self._analyze_treasury_yield()
            score += yield_score * 0.1
            if yield_factor:
                factors.append(yield_factor)

        # 计算预测涨跌幅
        predicted_change = self._score_to_change(score)

        # 确定方向和置信度
        direction = self._get_direction(score)
        confidence = self._get_confidence(abs(score))

        # 生成摘要
        summary = self._generate_summary(index_name, predicted_change, direction, factors)

        # 保存到数据库
        now = datetime.utcnow()
        prediction = IndexPrediction(
            index_code=index_code,
            index_name=index_name,
            current_price=current_price,
            predicted_change=predicted_change,
            confidence=confidence,
            direction=direction,
            factors=factors,
            summary=summary,
            predicted_at=now,
            expires_at=now + timedelta(hours=48),
        )

        self.db.add(prediction)
        self.db.commit()

        logger.info(f"生成预测: {index_code} -> {predicted_change:+.2f}% ({direction})")

        return prediction.to_dict()

    def _analyze_price_trend(self, index_code: str) -> tuple:
        """分析近期价格趋势"""
        # 查询最近7天的历史数据
        since = datetime.utcnow() - timedelta(days=7)
        records = self.db.query(IndexQuote).filter(
            IndexQuote.index_code == index_code,
            IndexQuote.recorded_at >= since,
        ).order_by(IndexQuote.recorded_at.asc()).all()

        if len(records) < 2:
            return 0, None

        # 计算趋势
        first_price = records[0].price
        last_price = records[-1].price

        if first_price <= 0:
            return 0, None

        change_pct = (last_price - first_price) / first_price * 100

        # 评分: 上涨趋势给正分，下跌给负分
        score = min(max(change_pct * 10, -30), 30)

        if abs(change_pct) > 0.5:
            direction = "上涨" if change_pct > 0 else "下跌"
            return score, {
                "type": "trend",
                "label": f"近期趋势{direction}",
                "value": f"{change_pct:+.2f}%",
                "impact": "positive" if change_pct > 0 else "negative",
            }

        return score, None

    def _analyze_fund_flow(self) -> tuple:
        """分析北向资金流向"""
        # 查询最近3天的资金流向
        since = datetime.utcnow() - timedelta(days=3)
        records = self.db.query(FundFlowHistory).filter(
            FundFlowHistory.flow_type == "north",
            FundFlowHistory.recorded_at >= since,
        ).order_by(FundFlowHistory.recorded_at.desc()).limit(10).all()

        if not records:
            return 0, None

        # 计算累计净流入
        total_flow = sum(r.total for r in records if r.total is not None)
        avg_flow = total_flow / len(records)

        # 评分: 净流入给正分
        score = min(max(avg_flow * 2, -25), 25)

        if abs(avg_flow) > 5:
            direction = "净流入" if avg_flow > 0 else "净流出"
            return score, {
                "type": "fund_flow",
                "label": f"北向资金{direction}",
                "value": f"{avg_flow:+.1f}亿",
                "impact": "positive" if avg_flow > 0 else "negative",
            }

        return score, None

    def _analyze_premium(self, index_code: str) -> tuple:
        """分析QDII溢价率"""
        # 映射指数到溢价率类型
        premium_mapping = {
            "sp500": "sp500",
            "nasdaq100": "nasdaq100",
            "hsi": "hsi",
        }

        if index_code not in premium_mapping:
            return 0, None

        # 查询最近的溢价率数据
        since = datetime.utcnow() - timedelta(hours=24)
        records = self.db.query(PremiumHistory).filter(
            PremiumHistory.recorded_at >= since,
        ).all()

        if not records:
            return 0, None

        # 计算平均溢价率
        avg_premium = sum(r.premium_rate for r in records if r.premium_rate) / len(records)

        # 高溢价通常预示短期回调风险，低溢价/折价可能有反弹空间
        # 溢价率反向影响评分
        score = min(max(-avg_premium * 5, -20), 20)

        if abs(avg_premium) > 1:
            status = "高溢价" if avg_premium > 0 else "折价"
            impact = "negative" if avg_premium > 2 else ("positive" if avg_premium < -1 else "neutral")
            return score, {
                "type": "premium",
                "label": f"QDII{status}",
                "value": f"{avg_premium:+.2f}%",
                "impact": impact,
            }

        return score, None

    def _analyze_momentum(self, quote: Dict) -> tuple:
        """分析当日动量"""
        change_pct = quote.get("change_percent", 0)

        # 动量延续效应
        score = min(max(change_pct * 8, -25), 25)

        if abs(change_pct) > 0.5:
            direction = "上涨" if change_pct > 0 else "下跌"
            return score, {
                "type": "momentum",
                "label": f"今日{direction}动量",
                "value": f"{change_pct:+.2f}%",
                "impact": "positive" if change_pct > 0 else "negative",
            }

        return score, None

    def _analyze_vix(self) -> tuple:
        """分析VIX恐慌指数"""
        vix = getattr(self, 'market_indicators', {}).get('vix')
        if not vix:
            return 0, None

        value = vix.get('value', 0)
        change_pct = vix.get('change_percent', 0)

        # VIX 高位通常意味着市场恐慌，可能反弹
        # VIX 低位可能意味着自满，需要警惕
        if value > 30:
            # 极度恐慌，可能超卖反弹
            score = 15
            impact = "positive"
            label = "VIX极高(超卖)"
        elif value > 25:
            score = -10
            impact = "negative"
            label = "VIX偏高(恐慌)"
        elif value > 20:
            score = -5
            impact = "negative"
            label = "VIX升高(谨慎)"
        elif value < 12:
            # 过度自满，可能回调
            score = -10
            impact = "negative"
            label = "VIX极低(自满)"
        else:
            score = 5
            impact = "positive"
            label = "VIX正常"

        # VIX变化方向也很重要
        if change_pct > 10:
            score -= 10
        elif change_pct < -10:
            score += 10

        return score, {
            "type": "vix",
            "label": label,
            "value": f"{value:.1f}",
            "impact": impact,
        }

    def _analyze_dxy(self, index_code: str) -> tuple:
        """分析美元指数"""
        dxy = getattr(self, 'market_indicators', {}).get('dxy')
        if not dxy:
            return 0, None

        value = dxy.get('value', 0)
        change_pct = dxy.get('change_percent', 0)

        # 美元走强通常对美股有压力，对港股/A股影响复杂
        # 美元走弱通常利好新兴市场

        if index_code in ["sp500", "nasdaq100"]:
            # 美股：美元走强有压力
            if change_pct > 0.5:
                score = -10
                impact = "negative"
                label = "美元走强"
            elif change_pct < -0.5:
                score = 10
                impact = "positive"
                label = "美元走弱"
            else:
                return 0, None
        elif index_code in ["hsi", "hstech"]:
            # 港股：美元走弱利好
            if change_pct > 0.5:
                score = -8
                impact = "negative"
                label = "美元走强"
            elif change_pct < -0.5:
                score = 8
                impact = "positive"
                label = "美元走弱"
            else:
                return 0, None
        else:
            # A股：影响相对较小
            if abs(change_pct) > 0.5:
                score = -5 if change_pct > 0 else 5
                impact = "negative" if change_pct > 0 else "positive"
                label = "美元走强" if change_pct > 0 else "美元走弱"
            else:
                return 0, None

        return score, {
            "type": "dxy",
            "label": label,
            "value": f"{value:.2f}",
            "impact": impact,
        }

    def _analyze_treasury_yield(self) -> tuple:
        """分析美债收益率"""
        treasury = getattr(self, 'market_indicators', {}).get('treasury_10y')
        yield_curve = getattr(self, 'market_indicators', {}).get('yield_curve')

        if not treasury:
            return 0, None

        yield_val = treasury.get('yield', 0)
        change = treasury.get('change', 0)

        score = 0
        factors = []

        # 收益率快速上升对股市不利
        if change > 0.05:
            score -= 15
            factors.append({
                "type": "treasury",
                "label": "10Y收益率上升",
                "value": f"{yield_val:.2f}%",
                "impact": "negative",
            })
        elif change < -0.05:
            score += 10
            factors.append({
                "type": "treasury",
                "label": "10Y收益率下降",
                "value": f"{yield_val:.2f}%",
                "impact": "positive",
            })

        # 收益率曲线倒挂是衰退信号
        if yield_curve and yield_curve.get('inverted'):
            score -= 10
            factors.append({
                "type": "yield_curve",
                "label": "收益率曲线倒挂",
                "value": f"{yield_curve['spread']:.2f}%",
                "impact": "negative",
            })

        if factors:
            return score, factors[0]  # 返回最重要的因素
        return 0, None

    def _score_to_change(self, score: float) -> float:
        """将评分转换为预测涨跌幅"""
        # score 范围约 -100 到 100
        # 转换为 -5% 到 5% 的预测涨跌幅
        return round(score / 20, 2)

    def _get_direction(self, score: float) -> str:
        """根据评分确定方向"""
        if score > 10:
            return "bullish"
        elif score < -10:
            return "bearish"
        return "neutral"

    def _get_confidence(self, abs_score: float) -> str:
        """根据评分绝对值确定置信度"""
        if abs_score > 40:
            return "high"
        elif abs_score > 20:
            return "medium"
        return "low"

    def _generate_summary(
        self,
        index_name: str,
        predicted_change: float,
        direction: str,
        factors: List[Dict]
    ) -> str:
        """生成预测摘要"""
        direction_text = {
            "bullish": "看涨",
            "bearish": "看跌",
            "neutral": "震荡",
        }.get(direction, "震荡")

        summary = f"{index_name}未来48小时预计{direction_text}"

        if predicted_change != 0:
            summary += f"，预测涨跌幅 {predicted_change:+.2f}%"

        if factors:
            factor_labels = [f["label"] for f in factors[:2]]
            summary += f"。主要因素：{', '.join(factor_labels)}"

        return summary

    def get_latest_predictions(self) -> List[Dict]:
        """获取最新的有效预测"""
        now = datetime.utcnow()

        predictions = []
        for index_code in INDEX_MAPPING.keys():
            record = self.db.query(IndexPrediction).filter(
                IndexPrediction.index_code == index_code,
                IndexPrediction.expires_at > now,
            ).order_by(IndexPrediction.predicted_at.desc()).first()

            if record:
                predictions.append(record.to_dict())

        return predictions


def generate_all_predictions(db: Session) -> List[Dict]:
    """生成所有指数预测（供定时任务调用）"""
    service = PredictionService(db)
    return service.generate_predictions()


def get_predictions(db: Session) -> List[Dict]:
    """获取最新预测（供API调用）"""
    service = PredictionService(db)
    return service.get_latest_predictions()
