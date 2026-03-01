export default function Header({ latency, cartSize }) {
    return (
        <header className="header" id="app-header">
            <div className="header-brand">
                <div className="header-logo">Z</div>
                <div>
                    <div className="header-title">CSAO Rail</div>
                    <div className="header-subtitle">Smart Add-On Recommendations</div>
                </div>
            </div>
            <div className="header-meta">
                <span className="header-badge badge-live">● LIVE</span>
                {latency > 0 && (
                    <span className="header-badge badge-latency">
                        ⚡ {latency.toFixed(0)}ms
                    </span>
                )}
                {cartSize > 0 && (
                    <span className="header-badge" style={{
                        background: 'rgba(226,55,68,0.15)',
                        color: '#ff6b6b',
                    }}>
                        🛒 {cartSize}
                    </span>
                )}
            </div>
        </header>
    );
}
