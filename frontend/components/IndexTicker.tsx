'use client';

import { useState, useEffect } from 'react';
import { IndexQuote } from '@/lib/api';

// 指数代码到中文名称的映射
const INDEX_NAMES: Record<string, string> = {
  sp500: '标普500',
  nasdaq100: '纳指100',
  csi300: '沪深300',
  star50: '科创50',
  hsi: '恒生指数',
  hstech: '恒生科技',
};

interface IndexTickerProps {
  indices: Record<string, IndexQuote>;
}

export default function IndexTicker({ indices }: IndexTickerProps) {
  const indexOrder = ['sp500', 'nasdaq100', 'csi300', 'star50', 'hsi'];

  return (
    <div className="flex items-center gap-4 overflow-x-auto py-2 px-4 bg-dark-card border-b border-dark-border">
      {indexOrder.map((code) => {
        const data = indices[code];
        if (!data) return null;

        const isPositive = data.change_percent >= 0;
        const colorClass = isPositive ? 'text-positive' : 'text-negative';

        return (
          <div
            key={code}
            className="flex items-center gap-2 whitespace-nowrap"
          >
            <span className="text-dark-muted text-sm">
              {INDEX_NAMES[code] || code}
            </span>
            <span className="text-dark-text font-medium">
              {data.price?.toFixed(2) || '-'}
            </span>
            <span className={`text-sm font-medium ${colorClass}`}>
              {isPositive ? '+' : ''}{data.change_percent?.toFixed(2) || '0'}%
            </span>
          </div>
        );
      })}
    </div>
  );
}
