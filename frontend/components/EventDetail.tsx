'use client';

import { Event } from '@/lib/api';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface EventDetailProps {
  event: Event | null;
}

export default function EventDetail({ event }: EventDetailProps) {
  if (!event) {
    return (
      <div className="flex items-center justify-center h-full text-dark-muted">
        <p>选择一个事件查看详情</p>
      </div>
    );
  }

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

  const stars = '★'.repeat(event.importance) + '☆'.repeat(5 - event.importance);

  // 格式化时间
  const formattedTime = format(new Date(event.created_at), 'yyyy-MM-dd HH:mm:ss', {
    locale: zhCN,
  });

  return (
    <div className="p-4 h-full overflow-y-auto">
      {/* 标题区 */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <span className={`tag ${impactClass}`}>{impactLabel}</span>
          <span className="importance-stars">{stars}</span>
        </div>
        <h2 className="text-xl font-semibold text-dark-text">
          {event.title}
        </h2>
        <p className="text-sm text-dark-muted mt-1">{formattedTime}</p>
      </div>

      {/* 摘要 */}
      {event.summary && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-dark-muted mb-1">摘要</h3>
          <p className="text-dark-text">{event.summary}</p>
        </div>
      )}

      {/* 详细数据 */}
      {event.data && Object.keys(event.data).length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-dark-muted mb-2">详细数据</h3>
          <div className="bg-dark-bg rounded-lg p-3 space-y-2">
            {Object.entries(event.data).map(([key, value]) => {
              // 跳过一些内部字段
              if (['recorded_at', 'alert_type'].includes(key)) return null;

              // 格式化显示
              let displayValue = value;
              if (typeof value === 'number') {
                displayValue = value.toFixed(2);
              }

              // 中文化 key
              const keyLabels: Record<string, string> = {
                fund_code: '基金代码',
                fund_name: '基金名称',
                premium_rate: '溢价率',
                price: '价格',
                nav: '净值',
                total: '合计',
                sh_connect: '沪股通',
                sz_connect: '深股通',
                change_percent: '涨跌幅',
              };

              return (
                <div key={key} className="flex justify-between">
                  <span className="text-dark-muted text-sm">
                    {keyLabels[key] || key}
                  </span>
                  <span className="text-dark-text text-sm font-medium">
                    {String(displayValue)}
                    {key.includes('rate') || key.includes('percent') ? '%' : ''}
                    {key.includes('connect') || key === 'total' ? '亿' : ''}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex gap-2 mt-6">
        <button
          onClick={() => {
            const text = `${event.title}\n${event.summary || ''}\n时间: ${formattedTime}`;
            navigator.clipboard.writeText(text);
          }}
          className="flex-1 py-2 px-4 text-sm bg-dark-border/50 text-dark-text rounded hover:bg-dark-border transition-colors"
        >
          复制内容
        </button>
        {event.source_url && (
          <a
            href={event.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 py-2 px-4 text-sm text-center bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            查看来源
          </a>
        )}
      </div>
    </div>
  );
}
