
export default function MenuItemCard({ item, isInCart, onAdd }) {
    const vegClass = item.veg_type === 'veg' ? 'veg' : 'non-veg';

    return (
        <div className={`menu-item ${isInCart ? 'in-cart' : ''}`} id={`menu-item-${item.item_id}`}>
            <div className="item-info">
                <div className="item-name">
                    <span className={`veg-badge ${vegClass}`} />
                    {item.name}
                </div>
                <div className="item-meta-row">
                    <span>★ {item.avg_rating}</span>
                    <span>·</span>
                    <span>{item.times_ordered} orders</span>
                </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="item-price">₹{item.base_price}</span>
                <button
                    className={`item-add-btn ${isInCart ? 'in-cart' : ''}`}
                    onClick={() => onAdd(item)}
                    aria-label={isInCart ? `Remove ${item.name}` : `Add ${item.name}`}
                >
                    {isInCart ? '✓' : '+'}
                </button>
            </div>
        </div>
    );
}
