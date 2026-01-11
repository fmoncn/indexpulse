/**
 * API 请求封装
 */

// API 基础地址 - 根据环境切换
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * 通用请求函数
 */
async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * 事件相关接口
 */
export interface Event {
  id: number;
  event_type: string;
  target_index: string;
  title: string;
  summary: string;
  impact: 'positive' | 'negative' | 'neutral';
  importance: number;
  source_url?: string;
  data?: Record<string, unknown>;
  created_at: string;
}

export interface EventsResponse {
  total: number;
  limit: number;
  offset: number;
  data: Event[];
}

export async function getEvents(params?: {
  limit?: number;
  offset?: number;
  event_type?: string;
  target_index?: string;
  min_importance?: number;
}): Promise<EventsResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  if (params?.event_type) searchParams.set('event_type', params.event_type);
  if (params?.target_index) searchParams.set('target_index', params.target_index);
  if (params?.min_importance) searchParams.set('min_importance', String(params.min_importance));

  const query = searchParams.toString();
  return request<EventsResponse>(`/events${query ? `?${query}` : ''}`);
}

/**
 * 溢价率相关接口
 */
export interface PremiumData {
  fund_code: string;
  fund_name: string;
  index_type: string;
  price: number;
  nav: number;
  nav_date: string;
  premium_rate: number;
  volume: number;
  increase_rt: number;
  recorded_at: string;
}

export interface PremiumResponse {
  updated_at: string;
  count: number;
  data: PremiumData[];
  grouped: Record<string, PremiumData[]>;
}

export async function getPremium(index_type?: string): Promise<PremiumResponse> {
  const query = index_type ? `?index_type=${index_type}` : '';
  return request<PremiumResponse>(`/premium${query}`);
}

/**
 * 资金流向相关接口
 */
export interface FundFlowData {
  flow_type: string;
  sh_connect: number;
  sz_connect: number;
  total: number;
  update_time?: string;
  recorded_at: string;
  hk_sh?: number;
  hk_sz?: number;
}

export interface FundFlowResponse {
  updated_at: string;
  north: FundFlowData | null;
  south: FundFlowData | null;
}

export async function getFundFlow(): Promise<FundFlowResponse> {
  return request<FundFlowResponse>('/fund-flow/realtime');
}

/**
 * 指数行情相关接口
 */
export interface IndexQuote {
  index_code: string;
  name: string;
  display_name?: string;
  price: number;
  change: number;
  change_percent: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  market_state?: string;
  recorded_at: string;
}

export interface IndicesResponse {
  updated_at: string;
  count: number;
  data: Record<string, IndexQuote>;
}

export async function getIndices(): Promise<IndicesResponse> {
  return request<IndicesResponse>('/indices');
}

/**
 * 系统状态接口
 */
export interface HealthResponse {
  status: string;
  scheduler: {
    running: boolean;
    jobs: Array<{
      id: string;
      name: string;
      next_run_time: string | null;
    }>;
  };
}

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}

/**
 * SWR fetcher
 */
export const fetcher = <T>(url: string): Promise<T> => request<T>(url);
