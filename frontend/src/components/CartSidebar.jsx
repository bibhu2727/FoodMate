import CSAORail from './CSAORail';

export default function CartSidebar({
    cart, recommendations, latency, recLoading,
    onRemove, onAddRecommended, isOpen, onClose, onCheckout
}) {
    const total = cart.reduce((sum, item) => sum + (item.base_price || item.price || 0), 0);


    return (
        <>
            <div className={`cart-overlay ${isOpen ? 'open' : ''}`} onClick={onClose} />

            <aside className={`cart-sidebar ${isOpen ? 'open' : ''}`} id="cart-sidebar">
                <div className="cart-header">
                    <div className="cart-title">
                        🛒 Your Cart
                        {cart.length > 0 && <span className="cart-count">{cart.length}</span>}
                    </div>
                </div>

                <div className="cart-items">
                    {cart.length === 0 ? (
                        <div className="cart-empty">
                            <div className="cart-empty-icon">🍽️</div>
                            <div className="cart-empty-text">Your cart is empty</div>
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                                Add items from the menu to get started
                            </div>
                        </div>
                    ) : (
                        cart.map((item, idx) => (
                            <div key={`${item.item_id}-${idx}`} className="cart-item">
                                <div className="cart-item-info">
                                    <div className="cart-item-name">
                                        <span className={`veg-badge ${item.veg_type === 'veg' ? 'veg' : 'non-veg'}`} />
                                        {item.name}
                                    </div>
                                    <div className="cart-item-price">₹{item.base_price || item.price}</div>
                                </div>
                                <button
                                    className="cart-item-remove"
                                    onClick={() => onRemove(idx)}
                                    aria-label={`Remove ${item.name}`}
                                >
                                    ✕
                                </button>
                            </div>
                        ))
                    )}
                </div>

                <CSAORail
                    recommendations={recommendations}
                    latency={latency}
                    loading={recLoading}
                    onAdd={onAddRecommended}
                />

                <div className="cart-footer">
                    <div className="cart-total-row">
                        <span className="cart-total-label">Total</span>
                        <span className="cart-total-value">₹{total}</span>
                    </div>
                    <button className="checkout-btn" disabled={cart.length === 0} id="checkout-btn" onClick={onCheckout}>
                        Proceed to Checkout →
                    </button>
                </div>
            </aside>
        </>
    );
}
