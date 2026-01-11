/**
 * 纯前端 API 模块 - 直接调用公开数据源
 */

// ============ 指数行情 (新浪财经) ============

interface IndexQuote {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  open: number;
  high: number;
  low: number;
  volume: number;
}

// 指数代码映射
const INDEX_CONFIG = {
  // 国内指数
  csi300: { sinaCode: 's_sh000300', name: '沪深300' },
  star50: { sinaCode: 's_sh000688', name: '科创50' },
  // 港股指数
  hsi: { sinaCode: 'rt_hkHSI', name: '恒生指数' },
  // 美股指数 (使用东方财富接口)
  sp500: { eastCode: '100.SPX', name: '标普500' },
  nasdaq100: { eastCode: '100.NDX', name: '纳斯达克100' },
};

/**
 * 获取新浪国内指数行情
 */
async function fetchSinaIndices(): Promise<Record<string, IndexQuote>> {
  const codes = ['s_sh000300', 's_sh000688'];
  const url = `https://hq.sinajs.cn/list=${codes.join(',')}`;

  try {
    const response = await fetch(url, {
      headers: { 'Referer': 'https://finance.sina.com.cn/' }
    });
    const text = await response.text();

    const results: Record<string, IndexQuote> = {};

    // 解析沪深300
    const csi300Match = text.match(/hq_str_s_sh000300="([^"]+)"/);
    if (csi300Match) {
      const parts = csi300Match[1].split(',');
      results.csi300 = {
        code: 'csi300',
        name: parts[0],
        price: parseFloat(parts[1]),
        change: parseFloat(parts[2]),
        changePercent: parseFloat(parts[3]),
        volume: parseFloat(parts[4]),
        open: 0, high: 0, low: 0,
      };
    }

    // 解析科创50
    const star50Match = text.match(/hq_str_s_sh000688="([^"]+)"/);
    if (star50Match) {
      const parts = star50Match[1].split(',');
      results.star50 = {
        code: 'star50',
        name: parts[0],
        price: parseFloat(parts[1]),
        change: parseFloat(parts[2]),
        changePercent: parseFloat(parts[3]),
        volume: parseFloat(parts[4]),
        open: 0, high: 0, low: 0,
      };
    }

    return results;
  } catch (error) {
    console.error('获取新浪指数失败:', error);
    return {};
  }
}

/**
 * 获取东方财富美股指数行情
 */
async function fetchEastMoneyUSIndices(): Promise<Record<string, IndexQuote>> {
  const results: Record<string, IndexQuote> = {};

  try {
    // 标普500
    const sp500Url = 'https://push2.eastmoney.com/api/qt/stock/get?secid=100.SPX&fields=f43,f44,f45,f46,f47,f57,f58,f169,f170';
    const sp500Res = await fetch(sp500Url);
    const sp500Data = await sp500Res.json();

    if (sp500Data?.data) {
      const d = sp500Data.data;
      results.sp500 = {
        code: 'sp500',
        name: '标普500',
        price: d.f43 / 100,
        change: d.f169 / 100,
        changePercent: d.f170 / 100,
        open: d.f46 / 100,
        high: d.f44 / 100,
        low: d.f45 / 100,
        volume: d.f47,
      };
    }

    // 纳斯达克100
    const ndxUrl = 'https://push2.eastmoney.com/api/qt/stock/get?secid=100.NDX&fields=f43,f44,f45,f46,f47,f57,f58,f169,f170';
    const ndxRes = await fetch(ndxUrl);
    const ndxData = await ndxRes.json();

    if (ndxData?.data) {
      const d = ndxData.data;
      results.nasdaq100 = {
        code: 'nasdaq100',
        name: '纳斯达克100',
        price: d.f43 / 100,
        change: d.f169 / 100,
        changePercent: d.f170 / 100,
        open: d.f46 / 100,
        high: d.f44 / 100,
        low: d.f45 / 100,
        volume: d.f47,
      };
    }

    // 恒生指数
    const hsiUrl = 'https://push2.eastmoney.com/api/qt/stock/get?secid=100.HSI&fields=f43,f44,f45,f46,f47,f57,f58,f169,f170';
    const hsiRes = await fetch(hsiUrl);
    const hsiData = await hsiRes.json();

    if (hsiData?.data) {
      const d = hsiData.data;
      results.hsi = {
        code: 'hsi',
        name: '恒生指数',
        price: d.f43 / 100,
        change: d.f169 / 100,
        changePercent: d.f170 / 100,
        open: d.f46 / 100,
        high: d.f44 / 100,
        low: d.f45 / 100,
        volume: d.f47,
      };
    }

    // 恒生科技指数
    const hstechUrl = 'https://push2.eastmoney.com/api/qt/stock/get?secid=100.HSTECH&fields=f43,f44,f45,f46,f47,f57,f58,f169,f170';
    const hstechRes = await fetch(hstechUrl);
    const hstechData = await hstechRes.json();

    if (hstechData?.data) {
      const d = hstechData.data;
      results.hstech = {
        code: 'hstech',
        name: '恒生科技',
        price: d.f43 / 100,
        change: d.f169 / 100,
        changePercent: d.f170 / 100,
        open: d.f46 / 100,
        high: d.f44 / 100,
        low: d.f45 / 100,
        volume: d.f47,
      };
    }
  } catch (error) {
    console.error('获取东方财富指数失败:', error);
  }

  return results;
}

/**
 * 获取所有指数行情
 */
export async function fetchAllIndices(): Promise<Record<string, IndexQuote>> {
  const [sina, east] = await Promise.all([
    fetchSinaIndices(),
    fetchEastMoneyUSIndices(),
  ]);

  return { ...sina, ...east };
}

// ============ 北向资金 (东方财富) ============

export interface FundFlow {
  shConnect: number;  // 沪股通 (亿)
  szConnect: number;  // 深股通 (亿)
  total: number;      // 合计 (亿)
  updateTime: string;
}

/**
 * 获取北向资金实时数据
 */
export async function fetchNorthFlow(): Promise<FundFlow | null> {
  try {
    const url = 'https://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56';
    const response = await fetch(url);
    const data = await response.json();

    if (!data?.data?.s2n) return null;

    const s2n = data.data.s2n;
    if (!s2n || s2n.length === 0) return null;

    // 获取最新一条数据
    const latest = s2n[s2n.length - 1];
    const parts = latest.split(',');

    if (parts.length < 4) return null;

    return {
      updateTime: parts[0],
      shConnect: parseFloat(parts[1]) / 10000,  // 万 -> 亿
      szConnect: parseFloat(parts[2]) / 10000,
      total: parseFloat(parts[3]) / 10000,
    };
  } catch (error) {
    console.error('获取北向资金失败:', error);
    return null;
  }
}

// ============ QDII溢价率 (东方财富) ============

export interface QDIIPremium {
  fundCode: string;
  fundName: string;
  price: number;        // 场内价格
  nav: number;          // 净值
  premiumRate: number;  // 溢价率 %
  changePercent: number; // 涨跌幅 %
  volume: number;       // 成交额（万）
  indexType: string;    // 对应指数
}

// 跟踪的QDII基金
const TRACKED_QDII: Record<string, { codes: string[], name: string }> = {
  sp500: { codes: ['513500', '159612'], name: '标普500' },
  nasdaq100: { codes: ['513100', '159941'], name: '纳斯达克100' },
  hsi: { codes: ['159920', '513660'], name: '恒生指数' },
};

/**
 * 获取单个ETF的实时数据
 */
async function fetchETFQuote(code: string): Promise<any> {
  try {
    // 判断是沪市还是深市
    const market = code.startsWith('51') || code.startsWith('56') ? '1' : '0';
    const secid = `${market}.${code}`;

    const url = `https://push2.eastmoney.com/api/qt/stock/get?secid=${secid}&fields=f43,f44,f45,f46,f47,f57,f58,f169,f170,f60`;
    const response = await fetch(url);
    const data = await response.json();

    if (data?.data) {
      return {
        code: code,
        price: data.data.f43 / 1000,      // 价格
        changePercent: data.data.f170 / 100, // 涨跌幅
        volume: data.data.f47 / 10000,     // 成交额（万）
        prevClose: data.data.f60 / 1000,   // 昨收
      };
    }
  } catch (error) {
    console.error(`获取ETF ${code} 数据失败:`, error);
  }
  return null;
}

/**
 * 获取基金净值
 */
async function fetchFundNav(code: string): Promise<number> {
  try {
    const url = `https://fundgz.1234567.com.cn/js/${code}.js?rt=${Date.now()}`;
    const response = await fetch(url);
    const text = await response.text();

    // 解析 jsonpgz({...})
    const match = text.match(/jsonpgz\((.+)\)/);
    if (match) {
      const data = JSON.parse(match[1]);
      return parseFloat(data.dwjz) || 0;  // 单位净值
    }
  } catch (error) {
    // 净值获取失败时返回0
  }
  return 0;
}

/**
 * 获取所有QDII溢价率数据
 */
export async function fetchQDIIPremiums(): Promise<QDIIPremium[]> {
  const results: QDIIPremium[] = [];

  for (const [indexType, config] of Object.entries(TRACKED_QDII)) {
    for (const code of config.codes) {
      try {
        const [quote, nav] = await Promise.all([
          fetchETFQuote(code),
          fetchFundNav(code),
        ]);

        if (quote) {
          // 计算溢价率
          let premiumRate = 0;
          if (nav > 0) {
            premiumRate = ((quote.price - nav) / nav) * 100;
          }

          results.push({
            fundCode: code,
            fundName: `${config.name}ETF`,
            price: quote.price,
            nav: nav,
            premiumRate: premiumRate,
            changePercent: quote.changePercent,
            volume: quote.volume,
            indexType: indexType,
          });
        }
      } catch (error) {
        console.error(`处理 ${code} 失败:`, error);
      }
    }
  }

  return results;
}

// ============ 导出类型 ============

export type { IndexQuote };

// ============ 48小时预测 ============

export interface IndexPrediction {
  index_code: string;
  index_name: string;
  current_price: number;
  predicted_change: number;  // 预测涨跌幅 %
  confidence: 'high' | 'medium' | 'low';
  direction: 'bullish' | 'bearish' | 'neutral';
  factors: {
    type: string;
    label: string;
    value: string;
    impact: 'positive' | 'negative' | 'neutral';
  }[];
  summary: string;
  predicted_at: string;
  expires_at: string;
}

// 后端 API 地址
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * 获取所有指数的48小时预测
 */
export async function fetchPredictions(): Promise<IndexPrediction[]> {
  try {
    const response = await fetch(`${API_BASE}/prediction`);
    const data = await response.json();
    return data.data || [];
  } catch (error) {
    console.error('获取预测数据失败:', error);
    return [];
  }
}

/**
 * 获取单个指数的48小时预测
 */
export async function fetchIndexPrediction(indexCode: string): Promise<IndexPrediction | null> {
  try {
    const response = await fetch(`${API_BASE}/prediction/${indexCode}`);
    const data = await response.json();
    return data.data || null;
  } catch (error) {
    console.error(`获取 ${indexCode} 预测失败:`, error);
    return null;
  }
}

// ============ 市场指标 ============

export interface MarketIndicators {
  vix: {
    value: number;
    change: number;
    change_percent: number;
    level: 'low' | 'normal' | 'elevated' | 'high';
    sentiment: string;
  } | null;
  dxy: {
    value: number;
    change: number;
    change_percent: number;
    trend: 'strong' | 'neutral' | 'weak';
    description: string;
  } | null;
  treasury_10y: {
    maturity: string;
    yield: number;
    change: number;
  } | null;
  treasury_2y: {
    maturity: string;
    yield: number;
    change: number;
  } | null;
  yield_curve: {
    spread: number;
    inverted: boolean;
    description: string;
  } | null;
  fear_greed: {
    score: number;
    level: string;
    description: string;
  } | null;
}

/**
 * 获取市场指标数据
 */
export async function fetchMarketIndicators(): Promise<MarketIndicators | null> {
  try {
    const response = await fetch(`${API_BASE}/market`);
    const data = await response.json();
    return data.data || null;
  } catch (error) {
    console.error('获取市场指标失败:', error);
    return null;
  }
}
