import { format, parseISO } from 'date-fns';
import { useState, type ReactElement } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';

import type { TimelineDataPoint } from '../../types/metrics.ts';
import './GrowthChart.css';

interface GrowthChartProps {
  data: TimelineDataPoint[];
}

type MetricKey = 'universities' | 'researchers' | 'students';

const METRIC_COLORS: Record<MetricKey, string> = {
  universities: '#8b5cf6',
  researchers: '#10b981',
  students: '#f59e0b',
};

const ALL_METRICS: MetricKey[] = ['universities', 'researchers', 'students'];

const AXIS_STYLE = {
  tick: { fontSize: 12, fill: '#6b7280' },
  axisLine: { stroke: '#e5e7eb' },
  tickLine: { stroke: '#e5e7eb' },
};

const TOOLTIP_STYLE = {
  backgroundColor: 'white',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
};

function formatDate(dateStr: string): string {
  try {
    return format(parseISO(dateStr), 'MMM d');
  } catch {
    return dateStr;
  }
}

function formatTooltipDate(dateStr: string): string {
  try {
    return format(parseISO(dateStr), 'MMM d, yyyy');
  } catch {
    return dateStr;
  }
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

interface MetricToggleProps {
  metric: MetricKey;
  isActive: boolean;
  onToggle: (metric: MetricKey) => void;
}

function MetricToggle({ metric, isActive, onToggle }: MetricToggleProps): ReactElement {
  const color = METRIC_COLORS[metric];
  return (
    <button
      key={metric}
      className={`toggle-btn ${isActive ? 'active' : ''}`}
      onClick={() => onToggle(metric)}
      style={{
        borderColor: isActive ? color : undefined,
        backgroundColor: isActive ? `${color}15` : undefined,
      }}
    >
      <span className="toggle-dot" style={{ backgroundColor: color }} />
      {capitalize(metric)}
    </button>
  );
}

interface MetricLineProps {
  metric: MetricKey;
  yAxisId: string;
}

function MetricLine({ metric, yAxisId }: MetricLineProps): ReactElement {
  const color = METRIC_COLORS[metric];
  return (
    <Line
      yAxisId={yAxisId}
      type="monotone"
      dataKey={metric}
      stroke={color}
      strokeWidth={2}
      dot={{ r: 4, fill: color }}
      activeDot={{ r: 6 }}
      name={capitalize(metric)}
    />
  );
}

export function GrowthChart({ data }: GrowthChartProps): ReactElement {
  const [activeMetrics, setActiveMetrics] = useState<MetricKey[]>(ALL_METRICS);

  function toggleMetric(metric: MetricKey): void {
    setActiveMetrics(prev =>
      prev.includes(metric)
        ? prev.filter(m => m !== metric)
        : [...prev, metric]
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="growth-chart-container">
        <h3>Growth Over Time</h3>
        <div className="no-data">
          No historical data available. Sync data to see growth trends.
        </div>
      </div>
    );
  }

  return (
    <div className="growth-chart-container">
      <div className="chart-header">
        <h3>Growth Over Time</h3>
        <div className="metric-toggles">
          {ALL_METRICS.map(metric => (
            <MetricToggle
              key={metric}
              metric={metric}
              isActive={activeMetrics.includes(metric)}
              onToggle={toggleMetric}
            />
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" tickFormatter={formatDate} {...AXIS_STYLE} />
          <YAxis yAxisId="left" {...AXIS_STYLE} />
          <YAxis yAxisId="right" orientation="right" {...AXIS_STYLE} />
          <Tooltip labelFormatter={formatTooltipDate} contentStyle={TOOLTIP_STYLE} />
          <Legend />

          {activeMetrics.map(metric => (
            <MetricLine
              key={metric}
              metric={metric}
              yAxisId={metric === 'universities' ? 'left' : 'right'}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
