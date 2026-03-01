import { useMemo } from 'react';
import MenuItemCard from './MenuItemCard';

const CATEGORY_ORDER = ['mains', 'sides', 'beverages', 'desserts'];
const CATEGORY_LABELS = {
    mains: '🍛 Mains',
    sides: '🥗 Sides',
    beverages: '🥤 Beverages',
    desserts: '🍰 Desserts',
};

export default function RestaurantMenu({ menu, cart, onToggleItem }) {
    const cartIds = useMemo(() => new Set(cart.map(c => c.item_id)), [cart]);

    const grouped = useMemo(() => {
        const groups = {};
        for (const item of menu) {
            const cat = item.category || 'mains';
            if (!groups[cat]) groups[cat] = [];
            groups[cat].push(item);
        }
        return groups;
    }, [menu]);

    return (
        <div className="menu-section" id="menu-section">
            {CATEGORY_ORDER.map(cat => {
                const items = grouped[cat];
                if (!items || items.length === 0) return null;

                return (
                    <div key={cat}>
                        <div className="menu-category-title">
                            {CATEGORY_LABELS[cat] || cat}
                        </div>
                        <div className="menu-grid">
                            {items.map(item => (
                                <MenuItemCard
                                    key={item.item_id}
                                    item={item}
                                    isInCart={cartIds.has(item.item_id)}
                                    onAdd={onToggleItem}
                                />
                            ))}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
