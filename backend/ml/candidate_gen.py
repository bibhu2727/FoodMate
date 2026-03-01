"""
Candidate Generation (Stage 1) for CSAO Recommendation System.
Uses item co-occurrence, popularity, and meal-pattern heuristics
to quickly narrow down candidates from the full menu.
"""
import json
import os
from collections import defaultdict, Counter


class CandidateGenerator:
    def __init__(self):
        self.cooccurrence = defaultdict(Counter)
        self.category_popularity = defaultdict(Counter)
        self.meal_patterns = defaultdict(Counter)
        self.is_trained = False

    def train(self, orders):
        """Build co-occurrence and popularity matrices from historical orders."""
        for order in orders:
            initial = order.get("initial_items", [])
            added = order.get("added_items", [])
            meal_time = order.get("meal_time", "lunch")

            initial_names = [item["name"] for item in initial]
            added_names = [item["name"] for item in added]

            for main_name in initial_names:
                for addon_name in added_names:
                    self.cooccurrence[main_name][addon_name] += 1

            for addon in added:
                cat = addon.get("category", "mains")
                self.category_popularity[cat][addon["name"]] += 1
                self.meal_patterns[meal_time][addon["name"]] += 1

        self.is_trained = True

    def generate_candidates(self, cart_items, menu, context=None, top_n=20):
        """
        Generate candidate add-on items from menu based on cart state.
        Returns at most top_n candidates ranked by co-occurrence + popularity.
        """
        cart_names = {item.get("name", "") for item in cart_items}
        cart_categories = {item.get("category", "mains") for item in cart_items}
        meal_time = context.get("meal_time", "lunch") if context else "lunch"

        candidate_scores = {}

        for item in menu:
            if item["name"] in cart_names:
                continue

            score = 0.0

            for cart_item in cart_items:
                cart_name = cart_item.get("name", "")
                cooc = self.cooccurrence.get(cart_name, {})
                score += cooc.get(item["name"], 0) * 2.0

            cat = item.get("category", "mains")
            cat_pop = self.category_popularity.get(cat, {})
            score += cat_pop.get(item["name"], 0) * 0.5

            meal_pop = self.meal_patterns.get(meal_time, {})
            score += meal_pop.get(item["name"], 0) * 0.3

            if cat not in cart_categories and cat in ["sides", "beverages", "desserts"]:
                score += 5.0

            pop = item.get("popularity_score", 0.5)
            score += pop * 3.0

            candidate_scores[item["name"]] = {
                "item": item,
                "candidate_score": score,
            }

        sorted_candidates = sorted(
            candidate_scores.values(),
            key=lambda x: x["candidate_score"],
            reverse=True,
        )

        return [c["item"] for c in sorted_candidates[:top_n]]

    def save(self, path):
        data = {
            "cooccurrence": {k: dict(v) for k, v in self.cooccurrence.items()},
            "category_popularity": {k: dict(v) for k, v in self.category_popularity.items()},
            "meal_patterns": {k: dict(v) for k, v in self.meal_patterns.items()},
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def load(self, path):
        if not os.path.exists(path):
            return False
        with open(path, "r") as f:
            data = json.load(f)
        self.cooccurrence = defaultdict(Counter, {k: Counter(v) for k, v in data["cooccurrence"].items()})
        self.category_popularity = defaultdict(Counter, {k: Counter(v) for k, v in data["category_popularity"].items()})
        self.meal_patterns = defaultdict(Counter, {k: Counter(v) for k, v in data["meal_patterns"].items()})
        self.is_trained = True
        return True
