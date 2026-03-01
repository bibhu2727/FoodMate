"""
Feature Engineering Pipeline for CSAO Recommendation System.
Transforms raw cart/user/restaurant/context data into ML-ready features.
Handles cold-start scenarios with fallback features.
"""
import numpy as np
from collections import Counter


CATEGORY_MAP = {"mains": 0, "sides": 1, "beverages": 2, "desserts": 3}
MEAL_TIME_MAP = {"breakfast": 0, "lunch": 1, "snacks": 2, "dinner": 3, "late_night": 4}
SEGMENT_MAP = {"budget": 0, "regular": 1, "premium": 2, "frequent": 3}
VEG_MAP = {"veg": 0, "non-veg": 1}
CITY_MAP = {
    "Mumbai": 0, "Delhi": 1, "Bangalore": 2, "Hyderabad": 3,
    "Chennai": 4, "Kolkata": 5, "Pune": 6, "Jaipur": 7,
}
CUISINE_MAP = {
    "North Indian": 0, "South Indian": 1, "Chinese": 2, "Italian": 3,
    "Biryani": 4, "Street Food": 5, "Desserts": 6, "Beverages": 7,
    "Mughlai": 8, "Continental": 9,
}


def extract_cart_features(cart_items):
    """Extract aggregated features from current cart state."""
    if not cart_items:
        return {
            "cart_size": 0,
            "cart_total": 0,
            "cart_avg_price": 0,
            "cart_max_price": 0,
            "cart_has_mains": 0,
            "cart_has_sides": 0,
            "cart_has_beverages": 0,
            "cart_has_desserts": 0,
            "cart_veg_ratio": 0.5,
            "cart_category_diversity": 0,
        }

    prices = [item.get("price", item.get("base_price", 0)) for item in cart_items]
    categories = [item.get("category", "mains") for item in cart_items]
    veg_types = [item.get("veg_type", "veg") for item in cart_items]

    cat_counts = Counter(categories)

    return {
        "cart_size": len(cart_items),
        "cart_total": sum(prices),
        "cart_avg_price": np.mean(prices) if prices else 0,
        "cart_max_price": max(prices) if prices else 0,
        "cart_has_mains": int("mains" in cat_counts),
        "cart_has_sides": int("sides" in cat_counts),
        "cart_has_beverages": int("beverages" in cat_counts),
        "cart_has_desserts": int("desserts" in cat_counts),
        "cart_veg_ratio": sum(1 for v in veg_types if v == "veg") / max(len(veg_types), 1),
        "cart_category_diversity": len(cat_counts),
    }


def extract_candidate_features(candidate, cart_features):
    """Extract features for a candidate add-on item relative to cart."""
    price = candidate.get("price", candidate.get("base_price", 0))
    category = candidate.get("category", "mains")

    cart_has_cat = cart_features.get(f"cart_has_{category}", 0)

    price_ratio = price / max(cart_features["cart_avg_price"], 1)

    return {
        "item_price": price,
        "item_category": CATEGORY_MAP.get(category, 0),
        "item_veg_type": VEG_MAP.get(candidate.get("veg_type", "veg"), 0),
        "item_popularity": candidate.get("popularity_score", 0.5),
        "item_avg_rating": candidate.get("avg_rating", 3.5),
        "item_times_ordered": candidate.get("times_ordered", 100),
        "price_ratio_to_cart": round(price_ratio, 3),
        "category_already_in_cart": cart_has_cat,
        "fills_meal_gap": int(not cart_has_cat and category in ["sides", "beverages", "desserts"]),
    }


def extract_context_features(context):
    """Extract temporal and geographic context features."""
    hour = context.get("hour", 12)

    return {
        "hour": hour,
        "is_lunch": int(11 <= hour <= 14),
        "is_dinner": int(19 <= hour <= 22),
        "is_late_night": int(hour >= 22 or hour < 2),
        "is_weekend": int(context.get("day_of_week", 0) >= 5),
        "meal_time": MEAL_TIME_MAP.get(context.get("meal_time", "lunch"), 1),
        "city": CITY_MAP.get(context.get("city", "Mumbai"), 0),
    }


def extract_user_features(user):
    """Extract user-level features with cold-start fallback."""
    is_new = user.get("is_new", True)

    return {
        "user_segment": SEGMENT_MAP.get(user.get("segment", "regular"), 1),
        "user_order_frequency": user.get("order_frequency", 5) if not is_new else 0,
        "user_avg_order_value": user.get("avg_order_value", 300) if not is_new else 300,
        "user_account_age": user.get("account_age_days", 0),
        "user_is_new": int(is_new),
        "user_diet_pref": VEG_MAP.get(user.get("diet_preference", "no_preference"), 0),
    }


def extract_restaurant_features(restaurant):
    """Extract restaurant-level features."""
    return {
        "rest_rating": restaurant.get("rating", 3.5),
        "rest_price_tier": {"budget": 0, "mid": 1, "premium": 2}.get(
            restaurant.get("price_tier", "mid"), 1
        ),
        "rest_cuisine": CUISINE_MAP.get(restaurant.get("cuisine_type", "North Indian"), 0),
        "rest_is_chain": int(restaurant.get("is_chain", False)),
        "rest_total_orders": restaurant.get("total_orders", 1000),
    }


def build_feature_vector(cart_items, candidate, context, user=None, restaurant=None):
    """Build complete feature vector for a candidate item."""
    cart_feats = extract_cart_features(cart_items)
    cand_feats = extract_candidate_features(candidate, cart_feats)
    ctx_feats = extract_context_features(context)

    features = {}
    features.update(cart_feats)
    features.update(cand_feats)
    features.update(ctx_feats)

    if user:
        features.update(extract_user_features(user))
    else:
        features.update(extract_user_features({"is_new": True}))

    if restaurant:
        features.update(extract_restaurant_features(restaurant))
    else:
        features.update(extract_restaurant_features({}))

    return features


FEATURE_NAMES = [
    "cart_size", "cart_total", "cart_avg_price", "cart_max_price",
    "cart_has_mains", "cart_has_sides", "cart_has_beverages", "cart_has_desserts",
    "cart_veg_ratio", "cart_category_diversity",
    "item_price", "item_category", "item_veg_type", "item_popularity",
    "item_avg_rating", "item_times_ordered", "price_ratio_to_cart",
    "category_already_in_cart", "fills_meal_gap",
    "hour", "is_lunch", "is_dinner", "is_late_night", "is_weekend",
    "meal_time", "city",
    "user_segment", "user_order_frequency", "user_avg_order_value",
    "user_account_age", "user_is_new", "user_diet_pref",
    "rest_rating", "rest_price_tier", "rest_cuisine", "rest_is_chain", "rest_total_orders",
]


def feature_dict_to_array(feature_dict):
    """Convert feature dictionary to ordered numpy array."""
    return np.array([feature_dict.get(f, 0) for f in FEATURE_NAMES], dtype=np.float32)
