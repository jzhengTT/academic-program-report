import { useEffect, useRef, type ReactElement } from 'react';

import { MetricCard } from '../components/dashboard/MetricCard.tsx';
import { SyncButton } from '../components/dashboard/SyncButton.tsx';
import { UniversityTable } from '../components/dashboard/UniversityTable.tsx';
import { useMetrics } from '../hooks/useMetrics.ts';
import { useSync } from '../hooks/useSync.ts';
import './Dashboard.css';

export function Dashboard(): ReactElement {
  // timeline is still being tracked but not displayed yet
  const { currentMetrics, timeline: _timeline, isLoading, error, refetch } = useMetrics();
  const { triggerSync } = useSync();
  const hasTriggeredInitialSync = useRef(false);

  // Auto-sync on mount
  useEffect(() => {
    if (hasTriggeredInitialSync.current) return;
    hasTriggeredInitialSync.current = true;
    triggerSync(false); // false = don't create snapshot
  }, [triggerSync]);

  if (error) {
    return (
      <div className="dashboard">
        <div className="error-banner">
          Failed to load dashboard data. Make sure the backend is running.
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Academic Program Dashboard</h1>
          <p className="subtitle">Tenstorrent University Collaborations</p>
        </div>
        <SyncButton onSyncComplete={refetch} />
      </header>

      {isLoading ? (
        <div className="loading-state">Loading metrics...</div>
      ) : (
        <>
          <section className="metrics-grid">
            <MetricCard
              title="Universities Engaged"
              value={currentMetrics?.total_universities ?? 0}
              icon="university"
            />
            <MetricCard
              title="Universities with TT Hardware"
              value={currentMetrics?.universities_with_tt_hardware ?? 0}
              icon="university"
            />
            <MetricCard
              title="Researchers on TT Hardware"
              value={currentMetrics?.researchers_on_tt_hardware ?? 0}
              icon="researchers"
            />
            <MetricCard
              title="Students on TT Hardware"
              value={currentMetrics?.students_on_tt_hardware ?? 0}
              icon="students"
            />
          </section>

          {/* Temporarily hidden until more data is available */}
          {/* <section className="chart-section">
            <GrowthChart data={timeline?.data ?? []} />
          </section> */}

          <section className="table-section">
            <UniversityTable />
          </section>
        </>
      )}
    </div>
  );
}
