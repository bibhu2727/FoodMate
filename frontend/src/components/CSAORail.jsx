import { useMemo } from 'react';

function getScoreClass(score) {
    if (score >= 0.65) return 'score-high';
    if (score >= 0.4) return 'score-mid';
    return 'score-low';
}

export default function CSAORail({ recommendations, latency, loading, onAdd }) {
    if (loading) {
        return (
            <div className="csao-rail">
                <div className="csao-header">
                    <div className="csao-title">✨ Recommended Add-ons</div>
                </div>
                <div className="csao-items">
                    <div className="csao-empty">
                        <div className="loading-spinner" style={{ width: 24, height: 24, borderWidth: 2 }} />
                    </div>
                </div>
            </div>
        );
    }

    if (!recommendations || recommendations.length === 0) {
        return (
            <div className="csao-rail">
                <div className="csao-header">
                    <div className="csao-title">✨ Recommended Add-ons</div>
                </div>
                <div className="csao-empty">
                    Add items to cart to see recommendations
                </div>
            </div>
        );
    }

    return (
        <div className="csao-rail" id="csao-rail">
            <div className="csao-header">
                <div className="csao-title">✨ Recommended Add-ons</div>
                {latency > 0 && (
                    <span className="csao-latency">⚡ {latency.toFixed(0)}ms</span>
                )}
            </div>
            <div className="csao-items">
                {recommendations.map((item, idx) => (
                    <div
                        key={`${item.name}-${idx}`}
                        className="csao-item"
                        onClick={() => onAdd(item)}
                        role="button"
                        tabIndex={0}
                        id={`csao-item-${idx}`}
                    >
                        <div className="csao-item-info">
                            <div className="csao-item-name">
                                <span className={`veg-badge ${item.veg_type === 'veg' ? 'veg' : 'non-veg'}`} />
                                {item.name}
                            </div>
                            <div className="csao-item-meta">
                                <span>₹{item.base_price || item.price}</span>
                                <span>·</span>
                                <span>{item.category}</span>
                                <span className={`csao-item-score ${getScoreClass(item.score)}`}>
                                    {(item.score * 100).toFixed(0)}% match
                                </span>
                            </div>
                        </div>
                        <button
                            className="csao-add-btn"
                            onClick={(e) => { e.stopPropagation(); onAdd(item); }}
                            aria-label={`Add ${item.name}`}
                        >
                            +
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
