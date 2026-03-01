"""
Synthetic Data Generator for CSAO Recommendation System.
Generates realistic food delivery data: restaurants, menus, users, orders, interactions.
Captures city-wise behavior, peak hours, cuisine correlations, and meal-time patterns.
"""
import json
import random
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ─── Constants ────────────────────────────────────────────────────────────────

CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Jaipur"]

CUISINE_TYPES = [
    "North Indian", "South Indian", "Chinese", "Italian", "Biryani",
    "Street Food", "Desserts", "Beverages", "Mughlai", "Continental"
]

MEAL_TIMES = {
    "breakfast": (6, 10),
    "lunch": (11, 14),
    "snacks": (15, 17),
    "dinner": (19, 22),
    "late_night": (22, 2),
}

MENU_ITEMS_BY_CUISINE = {
    "North Indian": {
        "mains": [
            ("Butter Chicken", 280, "non-veg"), ("Paneer Tikka Masala", 240, "veg"),
            ("Dal Makhani", 200, "veg"), ("Chicken Tikka", 260, "non-veg"),
            ("Palak Paneer", 220, "veg"), ("Rogan Josh", 320, "non-veg"),
            ("Chole Bhature", 180, "veg"), ("Kadai Chicken", 290, "non-veg"),
            ("Malai Kofta", 250, "veg"), ("Tandoori Chicken", 300, "non-veg"),
        ],
        "sides": [
            ("Naan", 50, "veg"), ("Garlic Naan", 60, "veg"), ("Butter Roti", 40, "veg"),
            ("Laccha Paratha", 55, "veg"), ("Raita", 60, "veg"), ("Onion Salad", 30, "veg"),
        ],
        "beverages": [
            ("Lassi", 80, "veg"), ("Masala Chai", 50, "veg"), ("Buttermilk", 60, "veg"),
            ("Mango Shake", 120, "veg"), ("Cold Coffee", 100, "veg"),
        ],
        "desserts": [
            ("Gulab Jamun", 100, "veg"), ("Rasmalai", 120, "veg"),
            ("Gajar Ka Halwa", 110, "veg"), ("Kulfi", 90, "veg"),
        ],
    },
    "South Indian": {
        "mains": [
            ("Masala Dosa", 150, "veg"), ("Idli Sambar", 100, "veg"),
            ("Vada", 80, "veg"), ("Uttapam", 140, "veg"),
            ("Rava Dosa", 160, "veg"), ("Pongal", 120, "veg"),
            ("Chicken Chettinad", 300, "non-veg"), ("Fish Curry", 280, "non-veg"),
        ],
        "sides": [
            ("Coconut Chutney", 40, "veg"), ("Sambar", 50, "veg"),
            ("Medu Vada", 70, "veg"), ("Papad", 30, "veg"),
        ],
        "beverages": [
            ("Filter Coffee", 60, "veg"), ("Tender Coconut", 80, "veg"),
            ("Rasam", 50, "veg"), ("Jigarthanda", 100, "veg"),
        ],
        "desserts": [
            ("Payasam", 100, "veg"), ("Mysore Pak", 90, "veg"),
            ("Kesari", 80, "veg"),
        ],
    },
    "Chinese": {
        "mains": [
            ("Fried Rice", 180, "veg"), ("Hakka Noodles", 170, "veg"),
            ("Manchurian", 200, "veg"), ("Chilli Chicken", 250, "non-veg"),
            ("Kung Pao Chicken", 280, "non-veg"), ("Schezwan Noodles", 190, "veg"),
            ("Sweet Corn Soup", 120, "veg"), ("Dragon Chicken", 270, "non-veg"),
        ],
        "sides": [
            ("Spring Rolls", 140, "veg"), ("Dim Sum", 160, "veg"),
            ("Crispy Corn", 130, "veg"), ("Honey Chilli Potato", 150, "veg"),
        ],
        "beverages": [
            ("Lemon Iced Tea", 80, "veg"), ("Green Tea", 60, "veg"),
            ("Fresh Lime Soda", 70, "veg"),
        ],
        "desserts": [
            ("Date Pancake", 130, "veg"), ("Chocolate Spring Roll", 120, "veg"),
        ],
    },
    "Biryani": {
        "mains": [
            ("Chicken Biryani", 250, "non-veg"), ("Mutton Biryani", 350, "non-veg"),
            ("Veg Biryani", 200, "veg"), ("Egg Biryani", 220, "non-veg"),
            ("Hyderabadi Biryani", 300, "non-veg"), ("Lucknowi Biryani", 320, "non-veg"),
            ("Paneer Biryani", 230, "veg"), ("Prawn Biryani", 380, "non-veg"),
        ],
        "sides": [
            ("Mirchi Ka Salan", 80, "veg"), ("Raita", 60, "veg"),
            ("Onion Raita", 50, "veg"), ("Shorba", 70, "non-veg"),
            ("Papad", 30, "veg"), ("Boiled Egg", 30, "non-veg"),
        ],
        "beverages": [
            ("Buttermilk", 60, "veg"), ("Phirni", 90, "veg"),
            ("Rose Sharbat", 70, "veg"), ("Coke", 50, "veg"),
        ],
        "desserts": [
            ("Double Ka Meetha", 110, "veg"), ("Qubani Ka Meetha", 120, "veg"),
            ("Gulab Jamun", 100, "veg"),
        ],
    },
    "Italian": {
        "mains": [
            ("Margherita Pizza", 300, "veg"), ("Pepperoni Pizza", 380, "non-veg"),
            ("Pasta Alfredo", 280, "veg"), ("Penne Arrabbiata", 260, "veg"),
            ("Chicken Pasta", 320, "non-veg"), ("Lasagna", 350, "non-veg"),
            ("Risotto", 300, "veg"), ("Calzone", 340, "non-veg"),
        ],
        "sides": [
            ("Garlic Bread", 120, "veg"), ("Bruschetta", 150, "veg"),
            ("Caesar Salad", 180, "veg"), ("Soup of the Day", 130, "veg"),
        ],
        "beverages": [
            ("Cold Coffee", 120, "veg"), ("Lemonade", 90, "veg"),
            ("Sparkling Water", 80, "veg"), ("Iced Tea", 100, "veg"),
        ],
        "desserts": [
            ("Tiramisu", 200, "veg"), ("Panna Cotta", 180, "veg"),
            ("Chocolate Mousse", 170, "veg"),
        ],
    },
    "Street Food": {
        "mains": [
            ("Pav Bhaji", 120, "veg"), ("Vada Pav", 50, "veg"),
            ("Pani Puri", 80, "veg"), ("Bhel Puri", 70, "veg"),
            ("Dahi Puri", 90, "veg"), ("Sev Puri", 80, "veg"),
            ("Samosa", 40, "veg"), ("Kachori", 50, "veg"),
        ],
        "sides": [
            ("Green Chutney", 20, "veg"), ("Tamarind Chutney", 20, "veg"),
            ("Masala Papad", 40, "veg"),
        ],
        "beverages": [
            ("Sugarcane Juice", 50, "veg"), ("Nimbu Pani", 40, "veg"),
            ("Masala Soda", 30, "veg"), ("Chai", 30, "veg"),
        ],
        "desserts": [
            ("Jalebi", 60, "veg"), ("Rabri", 80, "veg"), ("Kulfi", 70, "veg"),
        ],
    },
    "Mughlai": {
        "mains": [
            ("Seekh Kebab", 260, "non-veg"), ("Chicken Korma", 300, "non-veg"),
            ("Mutton Nihari", 350, "non-veg"), ("Shami Kebab", 240, "non-veg"),
            ("Paneer Nawabi", 250, "veg"), ("Galouti Kebab", 280, "non-veg"),
        ],
        "sides": [
            ("Roomali Roti", 50, "veg"), ("Sheermal", 60, "veg"),
            ("Mint Raita", 50, "veg"),
        ],
        "beverages": [
            ("Thandai", 90, "veg"), ("Rooh Afza", 60, "veg"),
            ("Lassi", 80, "veg"),
        ],
        "desserts": [
            ("Shahi Tukda", 130, "veg"), ("Phirni", 100, "veg"),
            ("Gulab Jamun", 100, "veg"),
        ],
    },
    "Continental": {
        "mains": [
            ("Grilled Chicken", 320, "non-veg"), ("Fish and Chips", 350, "non-veg"),
            ("Mushroom Risotto", 280, "veg"), ("Steak", 450, "non-veg"),
            ("Grilled Paneer", 260, "veg"), ("BBQ Wings", 300, "non-veg"),
        ],
        "sides": [
            ("French Fries", 120, "veg"), ("Coleslaw", 80, "veg"),
            ("Mashed Potato", 110, "veg"), ("Garden Salad", 100, "veg"),
        ],
        "beverages": [
            ("Smoothie", 140, "veg"), ("Milkshake", 150, "veg"),
            ("Fresh Juice", 120, "veg"), ("Iced Coffee", 130, "veg"),
        ],
        "desserts": [
            ("Brownie", 150, "veg"), ("Cheesecake", 200, "veg"),
            ("Ice Cream Sundae", 180, "veg"),
        ],
    },
    "Desserts": {
        "mains": [
            ("Chocolate Cake", 250, "veg"), ("Red Velvet Cake", 280, "veg"),
            ("Pastry Assortment", 200, "veg"), ("Waffle", 220, "veg"),
            ("Pancake Stack", 200, "veg"), ("Donut Box", 180, "veg"),
        ],
        "sides": [
            ("Whipped Cream", 50, "veg"), ("Chocolate Sauce", 40, "veg"),
        ],
        "beverages": [
            ("Hot Chocolate", 120, "veg"), ("Coffee", 100, "veg"),
            ("Milkshake", 150, "veg"), ("Cold Coffee", 130, "veg"),
        ],
        "desserts": [
            ("Ice Cream", 100, "veg"), ("Churros", 140, "veg"),
        ],
    },
    "Beverages": {
        "mains": [
            ("Mojito", 150, "veg"), ("Smoothie Bowl", 200, "veg"),
            ("Bubble Tea", 180, "veg"), ("Cold Brew", 160, "veg"),
            ("Frappe", 170, "veg"), ("Matcha Latte", 190, "veg"),
        ],
        "sides": [
            ("Cookie", 60, "veg"), ("Muffin", 80, "veg"),
        ],
        "beverages": [
            ("Espresso", 100, "veg"), ("Cappuccino", 140, "veg"),
            ("Latte", 150, "veg"), ("Americano", 120, "veg"),
        ],
        "desserts": [
            ("Brownie Bite", 90, "veg"), ("Energy Bar", 70, "veg"),
        ],
    },
}

USER_SEGMENTS = ["budget", "regular", "premium", "frequent"]
DIET_PREFS = ["veg", "non-veg", "no_preference"]


def generate_restaurants(n=50):
    restaurants = []
    for i in range(n):
        cuisine = random.choice(CUISINE_TYPES)
        city = random.choice(CITIES)
        price_tier = random.choice(["budget", "mid", "premium"])
        price_mult = {"budget": 0.8, "mid": 1.0, "premium": 1.3}[price_tier]
        is_chain = random.random() < 0.3

        restaurant = {
            "restaurant_id": f"R{i+1:04d}",
            "name": f"{cuisine} {'Express' if is_chain else 'Kitchen'} #{i+1}",
            "city": city,
            "cuisine_type": cuisine,
            "price_tier": price_tier,
            "price_multiplier": price_mult,
            "rating": round(random.uniform(3.2, 4.9), 1),
            "avg_delivery_time": random.randint(20, 55),
            "is_chain": is_chain,
            "total_orders": random.randint(500, 50000),
        }

        menu = []
        item_id = 0
        menu_template = MENU_ITEMS_BY_CUISINE.get(cuisine, MENU_ITEMS_BY_CUISINE["North Indian"])
        for category, items in menu_template.items():
            for name, base_price, veg_type in items:
                item_id += 1
                menu.append({
                    "item_id": f"{restaurant['restaurant_id']}_I{item_id:03d}",
                    "name": name,
                    "category": category,
                    "base_price": round(base_price * price_mult),
                    "veg_type": veg_type,
                    "popularity_score": round(random.uniform(0.1, 1.0), 2),
                    "avg_rating": round(random.uniform(3.0, 5.0), 1),
                    "times_ordered": random.randint(10, 5000),
                })
        restaurant["menu"] = menu
        restaurants.append(restaurant)
    return restaurants


def generate_users(n=500):
    users = []
    for i in range(n):
        city = random.choice(CITIES)
        segment = random.choices(USER_SEGMENTS, weights=[30, 40, 15, 15])[0]
        diet = random.choices(DIET_PREFS, weights=[35, 25, 40])[0]

        preferred_cuisines = random.sample(CUISINE_TYPES, k=random.randint(2, 5))

        users.append({
            "user_id": f"U{i+1:05d}",
            "city": city,
            "segment": segment,
            "diet_preference": diet,
            "preferred_cuisines": preferred_cuisines,
            "order_frequency": random.randint(1, 30),
            "avg_order_value": round(random.uniform(150, 800), 0),
            "account_age_days": random.randint(1, 1500),
            "is_new": random.random() < 0.15,
        })
    return users


def _pick_complementary_items(menu, cart_items, n=3):
    """Pick items complementary to what's in cart — simulates real user behavior."""
    cart_categories = {item["category"] for item in cart_items}
    cart_names = {item["name"] for item in cart_items}

    complement_priority = []
    others = []

    for item in menu:
        if item["name"] in cart_names:
            continue
        if item["category"] not in cart_categories:
            complement_priority.append(item)
        else:
            others.append(item)

    complement_priority.sort(key=lambda x: x["popularity_score"], reverse=True)
    others.sort(key=lambda x: x["popularity_score"], reverse=True)

    candidates = complement_priority + others
    return candidates[:n]


def generate_orders(users, restaurants, n_orders=5000):
    orders = []
    interactions = []

    for oid in range(n_orders):
        user = random.choice(users)

        eligible_rests = [r for r in restaurants if r["city"] == user["city"]]
        if not eligible_rests:
            eligible_rests = restaurants

        pref_rests = [r for r in eligible_rests if r["cuisine_type"] in user["preferred_cuisines"]]
        if pref_rests and random.random() < 0.7:
            rest = random.choice(pref_rests)
        else:
            rest = random.choice(eligible_rests)

        menu = rest["menu"]
        if user["diet_preference"] == "veg":
            available = [m for m in menu if m["veg_type"] == "veg"]
        elif user["diet_preference"] == "non-veg":
            available = menu
        else:
            available = menu

        if not available:
            available = menu

        hour = random.choices(
            list(range(24)),
            weights=[1,1,1,1,1,1,3,5,6,5,4,8,10,9,5,6,7,6,8,12,14,10,5,2],
        )[0]
        day_of_week = random.randint(0, 6)

        meal_time = "snacks"
        for mt, (start, end) in MEAL_TIMES.items():
            if start <= end:
                if start <= hour < end:
                    meal_time = mt
                    break
            else:
                if hour >= start or hour < end:
                    meal_time = mt
                    break

        mains = [m for m in available if m["category"] == "mains"]
        if not mains:
            mains = available
        n_main = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        selected_mains = random.sample(mains, k=min(n_main, len(mains)))

        cart_items = list(selected_mains)

        addon_candidates = _pick_complementary_items(available, cart_items, n=6)
        accepted_addons = []
        rejected_addons = []

        for candidate in addon_candidates:
            accept_prob = candidate["popularity_score"] * 0.5

            if candidate["category"] == "beverages" and not any(c["category"] == "beverages" for c in cart_items):
                accept_prob += 0.2
            if candidate["category"] == "sides" and not any(c["category"] == "sides" for c in cart_items):
                accept_prob += 0.15
            if candidate["category"] == "desserts":
                if meal_time in ["dinner", "lunch"]:
                    accept_prob += 0.1

            if user["segment"] == "premium":
                accept_prob += 0.1
            elif user["segment"] == "budget":
                accept_prob -= 0.1

            if random.random() < min(accept_prob, 0.85):
                accepted_addons.append(candidate)
                cart_items.append(candidate)
            else:
                rejected_addons.append(candidate)

        total_value = sum(item["base_price"] for item in cart_items)

        order_date = datetime.now() - timedelta(days=random.randint(0, 180))

        order = {
            "order_id": f"O{oid+1:06d}",
            "user_id": user["user_id"],
            "restaurant_id": rest["restaurant_id"],
            "city": rest["city"],
            "cuisine_type": rest["cuisine_type"],
            "meal_time": meal_time,
            "hour": hour,
            "day_of_week": day_of_week,
            "initial_items": [{"item_id": m["item_id"], "name": m["name"], "category": m["category"], "price": m["base_price"]} for m in selected_mains],
            "added_items": [{"item_id": a["item_id"], "name": a["name"], "category": a["category"], "price": a["base_price"]} for a in accepted_addons],
            "total_items": len(cart_items),
            "total_value": total_value,
            "order_date": order_date.strftime("%Y-%m-%d"),
        }
        orders.append(order)

        for addon in accepted_addons:
            interactions.append({
                "user_id": user["user_id"],
                "restaurant_id": rest["restaurant_id"],
                "item_id": addon["item_id"],
                "item_name": addon["name"],
                "item_category": addon["category"],
                "cart_items": [m["item_id"] for m in selected_mains],
                "cart_categories": list({m["category"] for m in selected_mains}),
                "label": 1,
                "meal_time": meal_time,
                "hour": hour,
                "day_of_week": day_of_week,
                "city": rest["city"],
                "user_segment": user["segment"],
                "order_date": order_date.strftime("%Y-%m-%d"),
            })

        for addon in rejected_addons:
            interactions.append({
                "user_id": user["user_id"],
                "restaurant_id": rest["restaurant_id"],
                "item_id": addon["item_id"],
                "item_name": addon["name"],
                "item_category": addon["category"],
                "cart_items": [m["item_id"] for m in selected_mains],
                "cart_categories": list({m["category"] for m in selected_mains}),
                "label": 0,
                "meal_time": meal_time,
                "hour": hour,
                "day_of_week": day_of_week,
                "city": rest["city"],
                "user_segment": user["segment"],
                "order_date": order_date.strftime("%Y-%m-%d"),
            })

    return orders, interactions


def generate_all(output_dir=None):
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(output_dir, exist_ok=True)

    print("Generating restaurants & menus...")
    restaurants = generate_restaurants(50)

    print("Generating users...")
    users = generate_users(500)

    print("Generating orders & interactions...")
    orders, interactions = generate_orders(users, restaurants, 5000)

    with open(os.path.join(output_dir, "restaurants.json"), "w") as f:
        json.dump(restaurants, f, indent=2)

    with open(os.path.join(output_dir, "users.json"), "w") as f:
        json.dump(users, f, indent=2)

    with open(os.path.join(output_dir, "orders.json"), "w") as f:
        json.dump(orders, f, indent=2)

    with open(os.path.join(output_dir, "interactions.json"), "w") as f:
        json.dump(interactions, f, indent=2)

    print(f"Generated: {len(restaurants)} restaurants, {len(users)} users, {len(orders)} orders, {len(interactions)} interactions")
    print(f"Data saved to: {output_dir}")

    stats = {
        "restaurants": len(restaurants),
        "users": len(users),
        "orders": len(orders),
        "interactions": len(interactions),
        "positive_interactions": sum(1 for i in interactions if i["label"] == 1),
        "negative_interactions": sum(1 for i in interactions if i["label"] == 0),
        "cities": list(set(r["city"] for r in restaurants)),
        "cuisines": list(set(r["cuisine_type"] for r in restaurants)),
    }
    print(f"\nStats: {json.dumps(stats, indent=2)}")
    return restaurants, users, orders, interactions


if __name__ == "__main__":
    generate_all()
