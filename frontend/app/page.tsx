'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchAllIndices, fetchNorthFlow, fetchQDIIPremiums, fetchPredictions, fetchMarketIndicators, IndexQuote, FundFlow, QDIIPremium, IndexPrediction, MarketIndicators } from '@/lib/client-api';

// 指数名称映射
const INDEX_NAMES: Record<string, { name: string; flag: string }> = {
  sp500: { name: '标普500', flag: '🇺🇸' },
  nasdaq100: { name: '纳指100', flag: '🇺🇸' },
  csi300: { name: '沪深300', flag: '🇨🇳' },
  star50: { name: '科创50', flag: '🇨🇳' },
  hsi: { name: '恒生指数', flag: '🇭🇰' },
  hstech: { name: '恒生科技', flag: '🇭🇰' },
};

export default function HomePage() {
  const [indices, setIndices] = useState<Record<string, IndexQuote>>({});
  const [northFlow, setNorthFlow] = useState<FundFlow | null>(null);
  const [premiums, setPremiums] = useState<QDIIPremium[]>([]);
  const [predictions, setPredictions] = useState<IndexPrediction[]>([]);
  const [marketIndicators, setMarketIndicators] = useState<MarketIndicators | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'overview' | 'premium' | 'flow' | 'prediction' | 'market'>('overview');

  // 加载数据
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [indicesData, flowData, premiumData, predictionData, marketData] = await Promise.all([
        fetchAllIndices(),
        fetchNorthFlow(),
        fetchQDIIPremiums(),
        fetchPredictions(),
        fetchMarketIndicators(),
      ]);

      setIndices(indicesData);
      setNorthFlow(flowData);
      setPremiums(premiumData);
      setPredictions(predictionData);
      setMarketIndicators(marketData);
      setLastUpdate(new Date().toLocaleTimeString('zh-CN'));
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始加载
  useEffect(() => {
    loadData();
  }, [loadData]);

  // 自动刷新（每分钟）
  useEffect(() => {
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, [loadData]);

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#c9d1d9]">
      {/* 顶部标题栏 */}
      <header className="sticky top-0 z-10 bg-[#161b22] border-b border-[#30363d] px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">📊</span>
            <h1 className="text-lg font-bold">IndexPulse</h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#8b949e]">{lastUpdate}</span>
            <button
              onClick={loadData}
              disabled={loading}
              className="px-2 py-1 text-xs bg-[#30363d] rounded hover:bg-[#484f58] disabled:opacity-50"
            >
              {loading ? '...' : '刷新'}
            </button>
          </div>
        </div>
      </header>

      {/* 指数行情卡片 */}
      <section className="p-4">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {['sp500', 'nasdaq100', 'csi300', 'star50', 'hsi', 'hstech'].map((code) => {
            const data = indices[code];
            const info = INDEX_NAMES[code];
            const isPositive = data?.changePercent >= 0;

            return (
              <div
                key={code}
                className="bg-[#161b22] border border-[#30363d] rounded-lg p-3"
              >
                <div className="flex items-center gap-1 mb-1">
                  <span className="text-sm">{info?.flag}</span>
                  <span className="text-xs text-[#8b949e]">{info?.name}</span>
                </div>
                <div className="text-lg font-bold">
                  {data?.price?.toFixed(2) || '--'}
                </div>
                <div className={`text-sm font-medium ${isPositive ? 'text-[#3fb950]' : 'text-[#f85149]'}`}>
                  {isPositive ? '+' : ''}{data?.changePercent?.toFixed(2) || '0.00'}%
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Tab 切换 */}
      <div className="flex border-b border-[#30363d] px-4">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'overview'
              ? 'border-[#58a6ff] text-[#58a6ff]'
              : 'border-transparent text-[#8b949e]'
          }`}
        >
          概览
        </button>
        <button
          onClick={() => setActiveTab('premium')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'premium'
              ? 'border-[#58a6ff] text-[#58a6ff]'
              : 'border-transparent text-[#8b949e]'
          }`}
        >
          溢价率
        </button>
        <button
          onClick={() => setActiveTab('flow')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'flow'
              ? 'border-[#58a6ff] text-[#58a6ff]'
              : 'border-transparent text-[#8b949e]'
          }`}
        >
          资金流
        </button>
        <button
          onClick={() => setActiveTab('prediction')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'prediction'
              ? 'border-[#58a6ff] text-[#58a6ff]'
              : 'border-transparent text-[#8b949e]'
          }`}
        >
          48h预测
        </button>
        <button
          onClick={() => setActiveTab('market')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'market'
              ? 'border-[#58a6ff] text-[#58a6ff]'
              : 'border-transparent text-[#8b949e]'
          }`}
        >
          市场指标
        </button>
      </div>

      {/* Tab 内容 */}
      <div className="p-4">
        {activeTab === 'overview' && (
          <OverviewTab indices={indices} northFlow={northFlow} premiums={premiums} />
        )}
        {activeTab === 'premium' && (
          <PremiumTab premiums={premiums} />
        )}
        {activeTab === 'flow' && (
          <FlowTab northFlow={northFlow} />
        )}
        {activeTab === 'prediction' && (
          <PredictionTab predictions={predictions} />
        )}
        {activeTab === 'market' && (
          <MarketTab indicators={marketIndicators} />
        )}
      </div>
    </div>
  );
}

// 概览 Tab
function OverviewTab({
  indices,
  northFlow,
  premiums,
}: {
  indices: Record<string, IndexQuote>;
  northFlow: FundFlow | null;
  premiums: QDIIPremium[];
}) {
  // 找出高溢价的基金
  const highPremiums = premiums.filter((p) => Math.abs(p.premiumRate) > 1).slice(0, 3);

  return (
    <div className="space-y-4">
      {/* 北向资金卡片 */}
      {northFlow && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <h3 className="text-sm font-medium text-[#8b949e] mb-3">北向资金</h3>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-2xl font-bold">
                {northFlow.total >= 0 ? '+' : ''}{northFlow.total.toFixed(2)}
              </span>
              <span className="text-sm text-[#8b949e] ml-1">亿</span>
            </div>
            <div className={`text-sm px-2 py-1 rounded ${
              northFlow.total >= 0 ? 'bg-[#238636]/20 text-[#3fb950]' : 'bg-[#da3633]/20 text-[#f85149]'
            }`}>
              {northFlow.total >= 0 ? '净流入' : '净流出'}
            </div>
          </div>
          <div className="flex gap-4 mt-3 text-sm text-[#8b949e]">
            <span>沪股通: {northFlow.shConnect.toFixed(2)}亿</span>
            <span>深股通: {northFlow.szConnect.toFixed(2)}亿</span>
          </div>
        </div>
      )}

      {/* 溢价预警 */}
      {highPremiums.length > 0 && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <h3 className="text-sm font-medium text-[#8b949e] mb-3">溢价预警</h3>
          <div className="space-y-2">
            {highPremiums.map((p) => (
              <div key={p.fundCode} className="flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium">{p.fundCode}</span>
                  <span className="text-xs text-[#8b949e] ml-2">{p.fundName}</span>
                </div>
                <div className={`text-sm font-medium ${
                  p.premiumRate >= 0 ? 'text-[#f85149]' : 'text-[#3fb950]'
                }`}>
                  {p.premiumRate >= 0 ? '+' : ''}{p.premiumRate.toFixed(2)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// 溢价率 Tab
function PremiumTab({ premiums }: { premiums: QDIIPremium[] }) {
  // 按指数类型分组
  const grouped: Record<string, QDIIPremium[]> = {};
  premiums.forEach((p) => {
    if (!grouped[p.indexType]) grouped[p.indexType] = [];
    grouped[p.indexType].push(p);
  });

  const indexOrder = ['sp500', 'nasdaq100', 'hsi'];

  return (
    <div className="space-y-4">
      {indexOrder.map((indexType) => {
        const items = grouped[indexType];
        if (!items || items.length === 0) return null;

        const info = INDEX_NAMES[indexType];

        return (
          <div key={indexType} className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden">
            <div className="bg-[#21262d] px-4 py-2 border-b border-[#30363d]">
              <span className="text-sm">{info?.flag} {info?.name}</span>
            </div>
            <div className="divide-y divide-[#30363d]">
              {items.map((p) => (
                <div key={p.fundCode} className="flex items-center justify-between px-4 py-3">
                  <div>
                    <div className="font-medium">{p.fundCode}</div>
                    <div className="text-xs text-[#8b949e]">
                      价格: {p.price.toFixed(3)} | 净值: {p.nav > 0 ? p.nav.toFixed(3) : '--'}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${
                      p.premiumRate > 1.5 ? 'text-[#f85149]' :
                      p.premiumRate < -1 ? 'text-[#3fb950]' :
                      'text-[#c9d1d9]'
                    }`}>
                      {p.premiumRate >= 0 ? '+' : ''}{p.premiumRate.toFixed(2)}%
                    </div>
                    <div className={`text-xs ${p.changePercent >= 0 ? 'text-[#3fb950]' : 'text-[#f85149]'}`}>
                      {p.changePercent >= 0 ? '+' : ''}{p.changePercent.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {premiums.length === 0 && (
        <div className="text-center py-8 text-[#8b949e]">
          暂无数据
        </div>
      )}
    </div>
  );
}

// 资金流 Tab
function FlowTab({ northFlow }: { northFlow: FundFlow | null }) {
  return (
    <div className="space-y-4">
      {/* 北向资金详情 */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
        <h3 className="text-sm font-medium text-[#8b949e] mb-4">北向资金（今日）</h3>

        {northFlow ? (
          <>
            <div className="text-center mb-6">
              <div className={`text-4xl font-bold ${
                northFlow.total >= 0 ? 'text-[#3fb950]' : 'text-[#f85149]'
              }`}>
                {northFlow.total >= 0 ? '+' : ''}{northFlow.total.toFixed(2)}
              </div>
              <div className="text-sm text-[#8b949e] mt-1">净流入（亿元）</div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-[#21262d] rounded-lg p-3 text-center">
                <div className="text-xs text-[#8b949e] mb-1">沪股通</div>
                <div className={`text-xl font-bold ${
                  northFlow.shConnect >= 0 ? 'text-[#3fb950]' : 'text-[#f85149]'
                }`}>
                  {northFlow.shConnect >= 0 ? '+' : ''}{northFlow.shConnect.toFixed(2)}
                </div>
              </div>
              <div className="bg-[#21262d] rounded-lg p-3 text-center">
                <div className="text-xs text-[#8b949e] mb-1">深股通</div>
                <div className={`text-xl font-bold ${
                  northFlow.szConnect >= 0 ? 'text-[#3fb950]' : 'text-[#f85149]'
                }`}>
                  {northFlow.szConnect >= 0 ? '+' : ''}{northFlow.szConnect.toFixed(2)}
                </div>
              </div>
            </div>

            <div className="text-center text-xs text-[#8b949e] mt-4">
              更新时间: {northFlow.updateTime}
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-[#8b949e]">
            非交易时段或数据加载中...
          </div>
        )}
      </div>

      {/* 说明 */}
      <div className="text-xs text-[#8b949e] text-center">
        数据来源：东方财富 | 仅供参考，不构成投资建议
      </div>
    </div>
  );
}

// 48小时预测 Tab
function PredictionTab({ predictions }: { predictions: IndexPrediction[] }) {
  const getDirectionColor = (direction: string) => {
    switch (direction) {
      case 'bullish': return 'text-[#3fb950]';
      case 'bearish': return 'text-[#f85149]';
      default: return 'text-[#8b949e]';
    }
  };

  const getDirectionText = (direction: string) => {
    switch (direction) {
      case 'bullish': return '看涨';
      case 'bearish': return '看跌';
      default: return '震荡';
    }
  };

  const getDirectionIcon = (direction: string) => {
    switch (direction) {
      case 'bullish': return '📈';
      case 'bearish': return '📉';
      default: return '📊';
    }
  };

  const getConfidenceBadge = (confidence: string) => {
    switch (confidence) {
      case 'high': return { text: '高', class: 'bg-[#238636]/30 text-[#3fb950]' };
      case 'medium': return { text: '中', class: 'bg-[#9e6a03]/30 text-[#d29922]' };
      default: return { text: '低', class: 'bg-[#6e7681]/30 text-[#8b949e]' };
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'positive': return 'text-[#3fb950]';
      case 'negative': return 'text-[#f85149]';
      default: return 'text-[#8b949e]';
    }
  };

  return (
    <div className="space-y-4">
      {predictions.length > 0 ? (
        predictions.map((p) => {
          const info = INDEX_NAMES[p.index_code];
          const confidence = getConfidenceBadge(p.confidence);

          return (
            <div
              key={p.index_code}
              className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden"
            >
              {/* 头部 */}
              <div className="bg-[#21262d] px-4 py-3 border-b border-[#30363d] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>{info?.flag}</span>
                  <span className="font-medium">{p.index_name}</span>
                  <span className="text-xs text-[#8b949e]">
                    {p.current_price?.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded ${confidence.class}`}>
                    置信度: {confidence.text}
                  </span>
                </div>
              </div>

              {/* 预测内容 */}
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getDirectionIcon(p.direction)}</span>
                    <div>
                      <div className={`text-xl font-bold ${getDirectionColor(p.direction)}`}>
                        {p.predicted_change >= 0 ? '+' : ''}{p.predicted_change?.toFixed(2)}%
                      </div>
                      <div className={`text-sm ${getDirectionColor(p.direction)}`}>
                        {getDirectionText(p.direction)}
                      </div>
                    </div>
                  </div>
                  <div className="text-right text-xs text-[#8b949e]">
                    <div>预测时间</div>
                    <div>{p.predicted_at ? new Date(p.predicted_at).toLocaleString('zh-CN') : '--'}</div>
                  </div>
                </div>

                {/* 影响因素 */}
                {p.factors && p.factors.length > 0 && (
                  <div className="mb-3">
                    <div className="text-xs text-[#8b949e] mb-2">影响因素</div>
                    <div className="flex flex-wrap gap-2">
                      {p.factors.map((factor, idx) => (
                        <div
                          key={idx}
                          className={`text-xs px-2 py-1 rounded bg-[#21262d] ${getImpactColor(factor.impact)}`}
                        >
                          {factor.label}: {factor.value}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 摘要 */}
                {p.summary && (
                  <div className="text-sm text-[#8b949e] border-t border-[#30363d] pt-3 mt-3">
                    {p.summary}
                  </div>
                )}
              </div>
            </div>
          );
        })
      ) : (
        <div className="text-center py-8 text-[#8b949e]">
          暂无预测数据，请稍后刷新
        </div>
      )}

      {/* 说明 */}
      <div className="text-xs text-[#8b949e] text-center">
        预测基于历史数据、资金流向、溢价率等综合分析 | 仅供参考，不构成投资建议
      </div>
    </div>
  );
}

// 市场指标 Tab
function MarketTab({ indicators }: { indicators: MarketIndicators | null }) {
  if (!indicators) {
    return (
      <div className="text-center py-8 text-[#8b949e]">
        加载市场指标中...
      </div>
    );
  }

  const getVixColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-[#3fb950]';
      case 'normal': return 'text-[#58a6ff]';
      case 'elevated': return 'text-[#d29922]';
      case 'high': return 'text-[#f85149]';
      default: return 'text-[#8b949e]';
    }
  };

  const getVixBg = (level: string) => {
    switch (level) {
      case 'low': return 'bg-[#238636]/20';
      case 'normal': return 'bg-[#1f6feb]/20';
      case 'elevated': return 'bg-[#9e6a03]/20';
      case 'high': return 'bg-[#da3633]/20';
      default: return 'bg-[#21262d]';
    }
  };

  return (
    <div className="space-y-4">
      {/* VIX 恐慌指数 */}
      {indicators.vix && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-[#8b949e]">VIX 恐慌指数</h3>
            <span className={`text-xs px-2 py-0.5 rounded ${getVixBg(indicators.vix.level)} ${getVixColor(indicators.vix.level)}`}>
              {indicators.vix.sentiment}
            </span>
          </div>
          <div className="flex items-end gap-3">
            <span className={`text-3xl font-bold ${getVixColor(indicators.vix.level)}`}>
              {indicators.vix.value.toFixed(2)}
            </span>
            <span className={`text-sm ${indicators.vix.change_percent >= 0 ? 'text-[#f85149]' : 'text-[#3fb950]'}`}>
              {indicators.vix.change_percent >= 0 ? '+' : ''}{indicators.vix.change_percent.toFixed(2)}%
            </span>
          </div>
          <div className="mt-3 text-xs text-[#8b949e]">
            VIX &lt; 15: 市场平静 | 15-20: 正常 | 20-30: 谨慎 | &gt; 30: 恐慌
          </div>
        </div>
      )}

      {/* 美元指数 */}
      {indicators.dxy && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-[#8b949e]">美元指数 DXY</h3>
            <span className="text-xs px-2 py-0.5 rounded bg-[#21262d] text-[#8b949e]">
              {indicators.dxy.description}
            </span>
          </div>
          <div className="flex items-end gap-3">
            <span className="text-3xl font-bold text-[#c9d1d9]">
              {indicators.dxy.value.toFixed(3)}
            </span>
            <span className={`text-sm ${indicators.dxy.change_percent >= 0 ? 'text-[#3fb950]' : 'text-[#f85149]'}`}>
              {indicators.dxy.change_percent >= 0 ? '+' : ''}{indicators.dxy.change_percent.toFixed(2)}%
            </span>
          </div>
        </div>
      )}

      {/* 美债收益率 */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
        <h3 className="text-sm font-medium text-[#8b949e] mb-3">美国国债收益率</h3>
        <div className="grid grid-cols-2 gap-4">
          {indicators.treasury_10y && (
            <div className="bg-[#21262d] rounded-lg p-3">
              <div className="text-xs text-[#8b949e] mb-1">10年期</div>
              <div className="text-xl font-bold text-[#c9d1d9]">
                {indicators.treasury_10y.yield.toFixed(3)}%
              </div>
              <div className={`text-xs ${indicators.treasury_10y.change >= 0 ? 'text-[#f85149]' : 'text-[#3fb950]'}`}>
                {indicators.treasury_10y.change >= 0 ? '+' : ''}{indicators.treasury_10y.change.toFixed(3)}
              </div>
            </div>
          )}
          {indicators.treasury_2y && (
            <div className="bg-[#21262d] rounded-lg p-3">
              <div className="text-xs text-[#8b949e] mb-1">2年期</div>
              <div className="text-xl font-bold text-[#c9d1d9]">
                {indicators.treasury_2y.yield.toFixed(3)}%
              </div>
              <div className={`text-xs ${indicators.treasury_2y.change >= 0 ? 'text-[#f85149]' : 'text-[#3fb950]'}`}>
                {indicators.treasury_2y.change >= 0 ? '+' : ''}{indicators.treasury_2y.change.toFixed(3)}
              </div>
            </div>
          )}
        </div>

        {/* 收益率曲线 */}
        {indicators.yield_curve && (
          <div className={`mt-3 p-2 rounded text-sm ${
            indicators.yield_curve.inverted
              ? 'bg-[#da3633]/20 text-[#f85149]'
              : 'bg-[#238636]/20 text-[#3fb950]'
          }`}>
            <span className="font-medium">收益率曲线利差: </span>
            <span>{indicators.yield_curve.spread.toFixed(3)}%</span>
            <span className="ml-2">({indicators.yield_curve.description})</span>
          </div>
        )}
      </div>

      {/* 市场情绪 */}
      {indicators.fear_greed && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <h3 className="text-sm font-medium text-[#8b949e] mb-3">市场情绪</h3>
          <div className="flex items-center gap-4">
            <div className="relative w-24 h-24">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#30363d"
                  strokeWidth="3"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke={indicators.fear_greed.score > 50 ? '#3fb950' : '#f85149'}
                  strokeWidth="3"
                  strokeDasharray={`${indicators.fear_greed.score}, 100`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold">{indicators.fear_greed.score}</span>
              </div>
            </div>
            <div>
              <div className="text-lg font-medium">{indicators.fear_greed.description}</div>
              <div className="text-xs text-[#8b949e] mt-1">
                0-25: 极度恐惧 | 25-45: 恐惧 | 45-55: 中性 | 55-75: 贪婪 | 75-100: 极度贪婪
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 说明 */}
      <div className="text-xs text-[#8b949e] text-center">
        数据来源: Yahoo Finance, 东方财富 | 仅供参考，不构成投资建议
      </div>
    </div>
  );
}
