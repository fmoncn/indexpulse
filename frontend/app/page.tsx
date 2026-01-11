'use client';

import { useState, useEffect, useCallback } from 'react';
import { fetchAllIndices, fetchNorthFlow, fetchQDIIPremiums, IndexQuote, FundFlow, QDIIPremium } from '@/lib/client-api';

// 指数名称映射
const INDEX_NAMES: Record<string, { name: string; flag: string }> = {
  sp500: { name: '标普500', flag: '🇺🇸' },
  nasdaq100: { name: '纳指100', flag: '🇺🇸' },
  csi300: { name: '沪深300', flag: '🇨🇳' },
  star50: { name: '科创50', flag: '🇨🇳' },
  hsi: { name: '恒生指数', flag: '🇭🇰' },
};

export default function HomePage() {
  const [indices, setIndices] = useState<Record<string, IndexQuote>>({});
  const [northFlow, setNorthFlow] = useState<FundFlow | null>(null);
  const [premiums, setPremiums] = useState<QDIIPremium[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'overview' | 'premium' | 'flow'>('overview');

  // 加载数据
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [indicesData, flowData, premiumData] = await Promise.all([
        fetchAllIndices(),
        fetchNorthFlow(),
        fetchQDIIPremiums(),
      ]);

      setIndices(indicesData);
      setNorthFlow(flowData);
      setPremiums(premiumData);
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
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {['sp500', 'nasdaq100', 'csi300', 'star50', 'hsi'].map((code) => {
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
