import { useState, useCallback, useRef, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api';

export function useRecommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [latency, setLatency] = useState(0);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef(null);

  const fetchRecommendations = useCallback(async (restaurantId, cartItems, context = {}) => {
    if (!restaurantId || cartItems.length === 0) {
      setRecommendations([]);
      setLatency(0);
      return;
    }

    if (abortRef.current) {
      abortRef.current.abort();
    }
    abortRef.current = new AbortController();

    setLoading(true);

    try {
      const now = new Date();
      const body = {
        restaurant_id: restaurantId,
        cart_items: cartItems.map(item => ({
          item_id: item.item_id || '',
          name: item.name,
          category: item.category || 'mains',
          price: item.base_price || item.price || 0,
          base_price: item.base_price || item.price || 0,
          veg_type: item.veg_type || 'veg',
          popularity_score: item.popularity_score || 0.5,
          avg_rating: item.avg_rating || 3.5,
          times_ordered: item.times_ordered || 100,
        })),
        hour: context.hour ?? now.getHours(),
        meal_time: context.meal_time || getMealTime(now.getHours()),
        city: context.city || 'Mumbai',
        top_n: 8,
      };

      const res = await fetch(`${API_BASE}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: abortRef.current.signal,
      });

      if (!res.ok) throw new Error('Failed to fetch recommendations');

      const data = await res.json();
      setRecommendations(data.recommendations || []);
      setLatency(data.latency_ms || 0);
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Recommendation error:', err);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  return { recommendations, latency, loading, fetchRecommendations };
}

function getMealTime(hour) {
  if (hour >= 6 && hour < 10) return 'breakfast';
  if (hour >= 11 && hour < 14) return 'lunch';
  if (hour >= 15 && hour < 17) return 'snacks';
  if (hour >= 19 && hour < 22) return 'dinner';
  if (hour >= 22 || hour < 2) return 'late_night';
  return 'snacks';
}
