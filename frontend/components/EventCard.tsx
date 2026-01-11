'use client';

import { Event } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// 事件类型映射
const EVENT_TYPE_LABELS: Record<string, { label: string; icon: string }> = {
  premium_alert: { label: '溢价预警', icon: '⚠️' },
  fund_flow: { label: '资金流向', icon: '💰' },
  index_move: { label: '指数异动', icon: '📊' },
  macro: { label: '宏观事件', icon: '🏛️' },
  announcement: { label: 'ETF公告', icon: '📢' },
};

// 指数类型映射
const INDEX_LABELS: Record<string, { label: string; flag: string }> = {
  sp500: { label: '标普500', flag: '🇺🇸' },
  nasdaq100: { label: '纳指100', flag: '🇺🇸' },
  csi300: { label: '沪深300', flag: '🇨🇳' },
  star50: { label: '科创50', flag: '🇨🇳' },
  hsi: { label: '恒生指数', flag: '🇭🇰' },
  hstech: { label: '恒生科技', flag: '🇭🇰' },
};

interface EventCardProps {
  event: Event;
  onClick?: (event: Event) => void;
  isSelected?: boolean;
}

export default function EventCard({ event, onClick, isSelected }: EventCardProps) {
  const eventTypeInfo = EVENT_TYPE_LABELS[event.event_type] || { label: event.event_type, icon: '📋' };
  const indexInfo = INDEX_LABELS[event.target_index] || { label: event.target_index, flag: '' };

  // 格式化时间
  const timeAgo = formatDistanceToNow(new Date(event.created_at), {
    addSuffix: true,
    locale: zhCN,
  });

  // 影响标签样式
  const impactClass = {
    positive: 'tag-positive',
    negative: 'tag-negative',
    neutral: 'tag-neutral',
  }[event.impact] || 'tag-neutral';

  const impactLabel = {
    positive: '利好',
    negative: '利空',
    neutral: '中性',
  }[event.impact] || '中性';

  // 重要性星星
  const stars = '★'.repeat(event.importance) + '☆'.repeat(5 - event.importance);

  return (
    <div
      className={`card cursor-pointer transition-all ${
        isSelected ? 'border-blue-500 bg-blue-500/10' : ''
      }`}
      onClick={() => onClick?.(event)}
    >
      {/* 头部：指数 + 事件类型 */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{indexInfo.flag}</span>
          <span className="text-dark-text font-medium">{indexInfo.label}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`tag ${impactClass}`}>{impactLabel}</span>
          <span className="text-dark-muted text-xs">{timeAgo}</span>
        </div>
      </div>

      {/* 标题 */}
      <h3 className="text-dark-text font-medium mb-2 line-clamp-2">
        {event.title}
      </h3>

      {/* 摘要 */}
      {event.summary && (
        <p className="text-dark-muted text-sm mb-3 line-clamp-2">
          {event.summary}
        </p>
      )}

      {/* 底部：事件类型 + 重要性 */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-1 text-dark-muted">
          <span>{eventTypeInfo.icon}</span>
          <span>{eventTypeInfo.label}</span>
        </div>
        <div className="importance-stars text-sm">
          {stars}
        </div>
      </div>
    </div>
  );
}
