import React, { useState } from 'react';

export default function CheckoutPage({ cart, onBack, onComplete }) {
    const [isProcessing, setIsProcessing] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    const total = cart.reduce((sum, item) => sum + (item.base_price || item.price || 0), 0);
    const tax = total * 0.05; // 5% GST
    const deliveryFee = total > 500 ? 0 : 40;
    const finalTotal = total + tax + deliveryFee;

    const handlePayment = () => {
        setIsProcessing(true);
        setTimeout(() => {
            setIsProcessing(false);
            setIsSuccess(true);
            setTimeout(() => {
                onComplete();
            }, 3000);
        }, 2000);
    };

    if (isSuccess) {
        return (
            <div className="checkout-container checkout-success">
                <div className="success-icon-wrapper">
                    <svg className="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                        <circle className="checkmark__circle" cx="26" cy="26" r="25" fill="none" />
                        <path className="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
                    </svg>
                </div>
                <h2>Order Confirmed!</h2>
                <p>Your food is being prepared and will be delivered shortly.</p>
                <div className="receipt-snippet">Order ID: #{Math.floor(Math.random() * 1000000)}</div>
            </div>
        );
    }

    return (
        <div className="checkout-container">
            <button className="back-btn" onClick={onBack}>← Back to Menu</button>
            <div className="checkout-layout">
                <div className="checkout-left">
                    <h2>Checkout</h2>

                    <div className="checkout-section glass-panel">
                        <h3>Delivery Address</h3>
                        <div className="address-card selected">
                            <div className="address-icon">📍</div>
                            <div className="address-details">
                                <strong>Home</strong>
                                <p>123 UI/UX Avenue, Design District, 400001</p>
                            </div>
                        </div>
                    </div>

                    <div className="checkout-section glass-panel">
                        <h3>Payment Method</h3>
                        <div className="payment-options">
                            <label className="payment-card">
                                <input type="radio" name="payment" defaultChecked />
                                <div className="card-design cc">
                                    <div className="chip"></div>
                                    <div className="cc-number">•••• •••• •••• 4242</div>
                                </div>
                                <span>Credit Card</span>
                            </label>
                            <label className="payment-card">
                                <input type="radio" name="payment" />
                                <div className="card-design upi">
                                    <div className="upi-logo">UPI</div>
                                </div>
                                <span>Google Pay / PhonePe</span>
                            </label>
                        </div>
                    </div>
                </div>

                <div className="checkout-right glass-panel">
                    <h3>Order Summary</h3>
                    <div className="order-summary-items">
                        {cart.map((item, idx) => (
                            <div key={`${item.item_id}-${idx}`} className="summary-item">
                                <span className={`veg-badge ${item.veg_type === 'veg' ? 'veg' : 'non-veg'}`} />
                                <span className="summary-item-name">{item.name}</span>
                                <span className="summary-item-price">₹{item.base_price || item.price}</span>
                            </div>
                        ))}
                    </div>

                    <div className="bill-details">
                        <div className="bill-row">
                            <span>Item Total</span>
                            <span>₹{total.toFixed(2)}</span>
                        </div>
                        <div className="bill-row">
                            <span>Taxes (5%)</span>
                            <span>₹{tax.toFixed(2)}</span>
                        </div>
                        <div className="bill-row">
                            <span>Delivery Fee</span>
                            <span>{deliveryFee === 0 ? <span className="free">FREE</span> : `₹${deliveryFee.toFixed(2)}`}</span>
                        </div>
                        <hr className="divider" />
                        <div className="bill-row grand-total">
                            <span>To Pay</span>
                            <span>₹{finalTotal.toFixed(2)}</span>
                        </div>
                    </div>

                    <button
                        className={`pay-btn ${isProcessing ? 'processing' : ''}`}
                        onClick={handlePayment}
                        disabled={isProcessing}
                    >
                        {isProcessing ? <div className="spinner-mini"></div> : `Pay ₹${finalTotal.toFixed(2)}`}
                    </button>
                    <div className="secure-badge">🔒 100% Secure Payment</div>
                </div>
            </div>
        </div>
    );
}
