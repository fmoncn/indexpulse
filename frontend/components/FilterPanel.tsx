'use client';

interface FilterPanelProps {
  selectedIndices: string[];
  selectedTypes: string[];
  minImportance: number;
  onIndicesChange: (indices: string[]) => void;
  onTypesChange: (types: string[]) => void;
  onImportanceChange: (importance: number) => void;
}

const INDICES = [
  { code: 'sp500', label: '标普500', flag: '🇺🇸' },
  { code: 'nasdaq100', label: '纳指100', flag: '🇺🇸' },
  { code: 'csi300', label: '沪深300', flag: '🇨🇳' },
  { code: 'star50', label: '科创50', flag: '🇨🇳' },
  { code: 'hsi', label: '恒生指数', flag: '🇭🇰' },
];

const EVENT_TYPES = [
  { code: 'premium_alert', label: '溢价预警', icon: '⚠️' },
  { code: 'fund_flow', label: '资金流向', icon: '💰' },
  { code: 'index_move', label: '指数异动', icon: '📊' },
];

export default function FilterPanel({
  selectedIndices,
  selectedTypes,
  minImportance,
  onIndicesChange,
  onTypesChange,
  onImportanceChange,
}: FilterPanelProps) {
  const toggleIndex = (code: string) => {
    if (selectedIndices.includes(code)) {
      onIndicesChange(selectedIndices.filter((i) => i !== code));
    } else {
      onIndicesChange([...selectedIndices, code]);
    }
  };

  const toggleType = (code: string) => {
    if (selectedTypes.includes(code)) {
      onTypesChange(selectedTypes.filter((t) => t !== code));
    } else {
      onTypesChange([...selectedTypes, code]);
    }
  };

  return (
    <div className="w-64 p-4 bg-dark-card border-r border-dark-border h-full overflow-y-auto">
      <h2 className="text-lg font-semibold text-dark-text mb-4">筛选</h2>

      {/* 指数选择 */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-dark-muted mb-2">指数</h3>
        <div className="space-y-1">
          {INDICES.map((index) => (
            <label
              key={index.code}
              className="flex items-center gap-2 py-1 px-2 rounded hover:bg-dark-border/30 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedIndices.length === 0 || selectedIndices.includes(index.code)}
                onChange={() => toggleIndex(index.code)}
                className="rounded border-dark-border bg-dark-bg text-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm">{index.flag}</span>
              <span className="text-sm text-dark-text">{index.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 事件类型 */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-dark-muted mb-2">事件类型</h3>
        <div className="space-y-1">
          {EVENT_TYPES.map((type) => (
            <label
              key={type.code}
              className="flex items-center gap-2 py-1 px-2 rounded hover:bg-dark-border/30 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedTypes.length === 0 || selectedTypes.includes(type.code)}
                onChange={() => toggleType(type.code)}
                className="rounded border-dark-border bg-dark-bg text-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm">{type.icon}</span>
              <span className="text-sm text-dark-text">{type.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 重要性筛选 */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-dark-muted mb-2">最低重要性</h3>
        <div className="space-y-1">
          {[1, 2, 3, 4, 5].map((level) => (
            <label
              key={level}
              className="flex items-center gap-2 py-1 px-2 rounded hover:bg-dark-border/30 cursor-pointer"
            >
              <input
                type="radio"
                name="importance"
                checked={minImportance === level}
                onChange={() => onImportanceChange(level)}
                className="border-dark-border bg-dark-bg text-blue-500 focus:ring-blue-500"
              />
              <span className="importance-stars text-sm">
                {'★'.repeat(level)}{'☆'.repeat(5 - level)}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* 重置按钮 */}
      <button
        onClick={() => {
          onIndicesChange([]);
          onTypesChange([]);
          onImportanceChange(1);
        }}
        className="w-full py-2 px-4 text-sm text-dark-muted border border-dark-border rounded hover:bg-dark-border/30 transition-colors"
      >
        重置筛选
      </button>
    </div>
  );
}
