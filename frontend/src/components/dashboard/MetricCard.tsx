import type { ReactElement } from 'react';

import './MetricCard.css';

type IconType = 'university' | 'researchers' | 'students';

interface MetricCardProps {
  title: string;
  value: number;
  growth?: number;
  icon: IconType;
}

const ICONS: Record<IconType, ReactElement> = {
  university: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2L2 7l10 5 10-5-10-5z" />
      <path d="M2 17l10 5 10-5" />
      <path d="M2 12l10 5 10-5" />
    </svg>
  ),
  researchers: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="9" cy="7" r="4" />
      <path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" />
      <circle cx="19" cy="11" r="2" />
      <path d="M19 8v1" />
      <path d="M19 13v1" />
    </svg>
  ),
  students: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
      <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5" />
    </svg>
  ),
};

function getGrowthClass(growth: number | undefined): string {
  if (growth === undefined || growth === 0) {
    return 'neutral';
  }
  return growth > 0 ? 'positive' : 'negative';
}

function formatGrowth(growth: number): string {
  const prefix = growth > 0 ? '+' : '';
  return `${prefix}${growth.toFixed(1)}%`;
}

export function MetricCard({ title, value, growth, icon }: MetricCardProps): ReactElement {
  return (
    <div className="metric-card">
      <div className="metric-icon">{ICONS[icon]}</div>
      <div className="metric-content">
        <h3 className="metric-title">{title}</h3>
        <div className="metric-value">{value.toLocaleString()}</div>
        {growth !== undefined && (
          <div className={`metric-growth ${getGrowthClass(growth)}`}>
            {formatGrowth(growth)}
            <span className="growth-period">vs 30 days ago</span>
          </div>
        )}
      </div>
    </div>
  );
}
