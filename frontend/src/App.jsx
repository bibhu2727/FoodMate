import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import RestaurantMenu from './components/RestaurantMenu';
import CartSidebar from './components/CartSidebar';
import MetricsDashboard from './components/MetricsDashboard';
import { useRecommendations } from './hooks/useRecommendations';
import './index.css';

const API_BASE = 'http://localhost:8000/api';

export default function App() {
  const [restaurants, setRestaurants] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);
  const [menu, setMenu] = useState([]);
  const [cart, setCart] = useState([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [appLoading, setAppLoading] = useState(true);
  const [error, setError] = useState(null);

  const { recommendations, latency, loading: recLoading, fetchRecommendations } = useRecommendations();

  useEffect(() => {
    const loadRestaurants = async () => {
      try {
        const res = await fetch(`${API_BASE}/restaurants`);
        if (!res.ok) throw new Error('Backend not available');
        const data = await res.json();
        setRestaurants(data.restaurants || []);
        if (data.restaurants?.length > 0) {
          selectRestaurant(data.restaurants[0].restaurant_id);
        }
      } catch (err) {
        setError('Cannot connect to backend. Please start the API server first.');
        console.error(err);
      } finally {
        setAppLoading(false);
      }
    };
    loadRestaurants();
  }, []);

  const selectRestaurant = async (restaurantId) => {
    try {
      const res = await fetch(`${API_BASE}/restaurants/${restaurantId}/menu`);
      if (!res.ok) throw new Error('Failed to load menu');
      const data = await res.json();
      setSelectedRestaurant(data);
      setMenu(data.menu || []);
      setCart([]);
    } catch (err) {
      console.error('Menu load error:', err);
    }
  };

  useEffect(() => {
    if (selectedRestaurant && cart.length > 0) {
      fetchRecommendations(selectedRestaurant.restaurant_id, cart, {
        city: selectedRestaurant.city,
      });
    }
  }, [cart, selectedRestaurant, fetchRecommendations]);

  const toggleItem = useCallback((item) => {
    setCart(prev => {
      const idx = prev.findIndex(c => c.item_id === item.item_id);
      if (idx >= 0) {
        return prev.filter((_, i) => i !== idx);
      }
      return [...prev, item];
    });
  }, []);

  const removeFromCart = useCallback((index) => {
    setCart(prev => prev.filter((_, i) => i !== index));
  }, []);

  const addRecommended = useCallback((recItem) => {
    setCart(prev => {
      if (prev.some(c => c.name === recItem.name)) return prev;
      return [...prev, {
        ...recItem,
        item_id: recItem.item_id || `rec_${recItem.name}`,
        base_price: recItem.base_price || recItem.price || 0,
      }];
    });
  }, []);

  if (appLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner" />
        <div className="loading-text">Loading CSAO Recommendation Engine...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="loading-container">
        <div style={{ fontSize: '3rem' }}>⚠️</div>
        <div className="loading-text" style={{ color: 'var(--accent-primary)' }}>{error}</div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: 400, textAlign: 'center' }}>
          Run <code style={{ background: 'var(--bg-card)', padding: '2px 6px', borderRadius: 4 }}>
            cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000
          </code> to start the backend.
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Header latency={latency} cartSize={cart.length} />

      {/* Restaurant Selector */}
      <div className="restaurant-selector" id="restaurant-selector">
        <div className="selector-label">Select Restaurant</div>
        <div className="restaurant-cards">
          {restaurants.slice(0, 12).map(rest => (
            <div
              key={rest.restaurant_id}
              className={`restaurant-card ${selectedRestaurant?.restaurant_id === rest.restaurant_id ? 'active' : ''}`}
              onClick={() => selectRestaurant(rest.restaurant_id)}
              id={`rest-card-${rest.restaurant_id}`}
            >
              <div className="rest-name">{rest.name}</div>
              <div className="rest-meta">
                <span className="rest-rating">★ {rest.rating}</span>
                <span className="rest-cuisine">{rest.cuisine_type}</span>
              </div>
              <div className="rest-meta" style={{ marginTop: '0.25rem' }}>
                <span>{rest.city}</span>
                <span>·</span>
                <span>{rest.price_tier}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-layout">
        <RestaurantMenu
          menu={menu}
          cart={cart}
          onToggleItem={toggleItem}
        />
        <CartSidebar
          cart={cart}
          recommendations={recommendations}
          latency={latency}
          recLoading={recLoading}
          onRemove={removeFromCart}
          onAddRecommended={addRecommended}
          isOpen={cartOpen}
          onClose={() => setCartOpen(false)}
        />
      </div>

      {/* Mobile Cart Toggle */}
      <button
        className="mobile-cart-toggle"
        onClick={() => setCartOpen(!cartOpen)}
        aria-label="Toggle cart"
      >
        🛒
        {cart.length > 0 && <span className="mobile-cart-badge">{cart.length}</span>}
      </button>

      {/* Metrics Dashboard */}
      <MetricsDashboard />
    </div>
  );
}
