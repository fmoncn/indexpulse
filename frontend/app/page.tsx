'use client';

import { useState, useEffect, useCallback } from 'react';
import IndexTicker from '@/components/IndexTicker';
import FilterPanel from '@/components/FilterPanel';
import EventCard from '@/components/EventCard';
import EventDetail from '@/components/EventDetail';
import { Event, IndexQuote, getEvents, getIndices } from '@/lib/api';

export default function HomePage() {
  // 状态
  const [events, setEvents] = useState<Event[]>([]);
  const [indices, setIndices] = useState<Record<string, IndexQuote>>({});
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 筛选状态
  const [selectedIndices, setSelectedIndices] = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [minImportance, setMinImportance] = useState(1);

  // 加载数据
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // 并行加载事件和指数数据
      const [eventsRes, indicesRes] = await Promise.all([
        getEvents({ limit: 50, min_importance: minImportance }),
        getIndices(),
      ]);

      setEvents(eventsRes.data || []);
      setIndices(indicesRes.data || {});
    } catch (err) {
      console.error('加载数据失败:', err);
      setError('加载数据失败，请检查后端服务是否运行');
    } finally {
      setLoading(false);
    }
  }, [minImportance]);

  // 初始加载
  useEffect(() => {
    loadData();
  }, [loadData]);

  // 自动刷新（每分钟）
  useEffect(() => {
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, [loadData]);

  // 筛选事件
  const filteredEvents = events.filter((event) => {
    // 指数筛选
    if (selectedIndices.length > 0 && !selectedIndices.includes(event.target_index)) {
      return false;
    }
    // 类型筛选
    if (selectedTypes.length > 0 && !selectedTypes.includes(event.event_type)) {
      return false;
    }
    // 重要性筛选
    if (event.importance < minImportance) {
      return false;
    }
    return true;
  });

  return (
    <div className="flex flex-col h-screen">
      {/* 顶部导航 */}
      <header className="flex items-center justify-between px-4 py-3 bg-dark-card border-b border-dark-border">
        <div className="flex items-center gap-2">
          <span className="text-xl">📊</span>
          <h1 className="text-xl font-bold text-dark-text">IndexPulse</h1>
          <span className="text-dark-muted text-sm">指数ETF情报中心</span>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={loadData}
            disabled={loading}
            className="px-3 py-1 text-sm bg-dark-border/50 text-dark-text rounded hover:bg-dark-border transition-colors disabled:opacity-50"
          >
            {loading ? '刷新中...' : '刷新'}
          </button>
        </div>
      </header>

      {/* 指数行情条 */}
      <IndexTicker indices={indices} />

      {/* 主内容区 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 左侧筛选器 */}
        <FilterPanel
          selectedIndices={selectedIndices}
          selectedTypes={selectedTypes}
          minImportance={minImportance}
          onIndicesChange={setSelectedIndices}
          onTypesChange={setSelectedTypes}
          onImportanceChange={setMinImportance}
        />

        {/* 中间事件流 */}
        <div className="flex-1 overflow-y-auto p-4 bg-dark-bg">
          {error ? (
            <div className="text-center py-8">
              <p className="text-negative mb-4">{error}</p>
              <button
                onClick={loadData}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                重试
              </button>
            </div>
          ) : loading && events.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <div className="loading"></div>
              <span className="ml-2 text-dark-muted">加载中...</span>
            </div>
          ) : filteredEvents.length === 0 ? (
            <div className="text-center py-8 text-dark-muted">
              <p>暂无事件</p>
              <p className="text-sm mt-2">调整筛选条件或等待新事件</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredEvents.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  onClick={setSelectedEvent}
                  isSelected={selectedEvent?.id === event.id}
                />
              ))}
            </div>
          )}
        </div>

        {/* 右侧详情面板 */}
        <div className="w-80 bg-dark-card border-l border-dark-border">
          <EventDetail event={selectedEvent} />
        </div>
      </div>
    </div>
  );
}
