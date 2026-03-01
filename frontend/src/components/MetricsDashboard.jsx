import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api';

export default function MetricsDashboard() {
    const [open, setOpen] = useState(false);
    const [metrics, setMetrics] = useState(null);
    const [featureImportance, setFeatureImportance] = useState(null);

    useEffect(() => {
        if (!open) return;

        const fetchMetrics = async () => {
            try {
                const [mRes, fiRes] = await Promise.all([
                    fetch(`${API_BASE}/metrics`),
                    fetch(`${API_BASE}/feature-importance`),
                ]);
                if (mRes.ok) setMetrics(await mRes.json());
                if (fiRes.ok) setFeatureImportance(await fiRes.json());
            } catch (err) {
                console.error('Metrics fetch error:', err);
            }
        };

        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000);
        return () => clearInterval(interval);
    }, [open]);

    const topFeatures = featureImportance
        ? Object.entries(featureImportance)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8)
        : [];

    const maxImportance = topFeatures.length > 0 ? topFeatures[0][1] : 1;

    return (
        <>
            <button
                className="metrics-toggle"
                onClick={() => setOpen(!open)}
                aria-label="Toggle metrics dashboard"
                id="metrics-toggle"
            >
                📊
            </button>

            {open && (
                <div className="metrics-panel" id="metrics-panel">
                    <div className="metrics-panel-title">System Metrics</div>

                    {metrics ? (
                        <div className="metrics-grid">
                            <div className="metric-card">
                                <div className="metric-label">Avg Latency</div>
                                <div className="metric-value accent">{metrics.avg_latency_ms}ms</div>
                            </div>
                            <div className="metric-card">
                                <div className="metric-label">P95 Latency</div>
                                <div className="metric-value warning">{metrics.p95_latency_ms}ms</div>
                            </div>
                            <div className="metric-card">
                                <div className="metric-label">Total Requests</div>
                                <div className="metric-value info">{metrics.total_requests}</div>
                            </div>
                            <div className="metric-card">
                                <div className="metric-label">SLA Compliance</div>
                                <div className="metric-value success">{metrics.sla_compliance}%</div>
                            </div>
                        </div>
                    ) : (
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>
                            Loading metrics...
                        </div>
                    )}

                    {topFeatures.length > 0 && (
                        <div className="fi-section">
                            <div className="fi-title">Top Feature Importance</div>
                            {topFeatures.map(([name, value]) => (
                                <div key={name} className="fi-bar-row">
                                    <span className="fi-bar-label">{name}</span>
                                    <div className="fi-bar-track">
                                        <div
                                            className="fi-bar-fill"
                                            style={{ width: `${(value / maxImportance) * 100}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </>
    );
}
