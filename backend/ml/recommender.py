"""
Unified Recommendation Engine for CSAO Rail.
Orchestrates Stage 1 (candidate generation) + Stage 2 (ranking).
Handles sequential cart updates and cold-start scenarios.
Optimized for <300ms latency.
"""
import time
import json
import os
import numpy as np

from .candidate_gen import CandidateGenerator
from .ranker import RankingModel


class RecommendationEngine:
    def __init__(self):
        self.candidate_gen = CandidateGenerator()
        self.ranker = RankingModel()
        self.restaurants = {}
        self.users = {}
        self.latency_history = []

    def load_data(self, data_dir):
        """Load restaurant and user data for inference."""
        rest_path = os.path.join(data_dir, "restaurants.json")
        user_path = os.path.join(data_dir, "users.json")

        if os.path.exists(rest_path):
            with open(rest_path) as f:
                rest_list = json.load(f)
                self.restaurants = {r["restaurant_id"]: r for r in rest_list}

        if os.path.exists(user_path):
            with open(user_path) as f:
                user_list = json.load(f)
                self.users = {u["user_id"]: u for u in user_list}

    def train(self, data_dir):
        """Full training pipeline: generate data if needed, train models."""
        orders_path = os.path.join(data_dir, "orders.json")
        interactions_path = os.path.join(data_dir, "interactions.json")

        if not os.path.exists(orders_path):
            from data.generator import generate_all
            generate_all(data_dir)

        self.load_data(data_dir)

        with open(orders_path) as f:
            orders = json.load(f)
        with open(interactions_path) as f:
            interactions = json.load(f)

        print("Training candidate generator...")
        self.candidate_gen.train(orders)

        print("Preparing ranking model training data...")
        X, y = self.ranker.prepare_training_data(
            interactions, self.restaurants, self.users
        )
        print(f"Training data shape: {X.shape}, Positive ratio: {y.mean():.3f}")

        print("Training ranking model...")
        X_val, y_val, val_preds = self.ranker.train(X, y)

        model_dir = os.path.join(data_dir, "models")
        os.makedirs(model_dir, exist_ok=True)
        self.candidate_gen.save(os.path.join(model_dir, "candidate_gen.json"))
        self.ranker.save(os.path.join(model_dir, "ranker.lgb"))

        print("Training complete! Models saved.")
        return {
            "training_samples": len(y),
            "positive_ratio": float(y.mean()),
            "feature_importance": self.ranker.get_feature_importance(),
        }

    def load_models(self, data_dir):
        """Load pre-trained models."""
        model_dir = os.path.join(data_dir, "models")
        self.load_data(data_dir)
        cg_loaded = self.candidate_gen.load(os.path.join(model_dir, "candidate_gen.json"))
        rk_loaded = self.ranker.load(os.path.join(model_dir, "ranker.lgb"))
        return cg_loaded and rk_loaded

    def recommend(self, restaurant_id, cart_items, context=None, user_id=None, top_n=10):
        """
        Generate recommendations for current cart state.
        Returns ranked list with scores and latency info.
        Handles sequential updates — call again when cart changes.
        """
        start_time = time.time()

        restaurant = self.restaurants.get(restaurant_id, {})
        menu = restaurant.get("menu", [])
        user = self.users.get(user_id) if user_id else None

        if context is None:
            from datetime import datetime
            now = datetime.now()
            hour = now.hour
            meal_time = "snacks"
            if 6 <= hour < 10: meal_time = "breakfast"
            elif 11 <= hour < 14: meal_time = "lunch"
            elif 15 <= hour < 17: meal_time = "snacks"
            elif 19 <= hour < 22: meal_time = "dinner"
            elif hour >= 22 or hour < 2: meal_time = "late_night"
            context = {
                "hour": hour,
                "day_of_week": now.weekday(),
                "meal_time": meal_time,
                "city": restaurant.get("city", "Mumbai"),
            }

        candidates = self.candidate_gen.generate_candidates(
            cart_items, menu, context, top_n=top_n * 2
        )

        scored = self.ranker.score_candidates(
            cart_items, candidates, context, user, restaurant
        )

        results = scored[:top_n]

        elapsed_ms = round((time.time() - start_time) * 1000, 1)
        self.latency_history.append(elapsed_ms)

        return {
            "recommendations": results,
            "latency_ms": elapsed_ms,
            "cart_size": len(cart_items),
            "candidates_evaluated": len(candidates),
            "model_version": "lgbm_v1",
        }

    def get_metrics(self):
        """Return operational metrics."""
        if not self.latency_history:
            return {"avg_latency_ms": 0, "p95_latency_ms": 0, "total_requests": 0}

        return {
            "avg_latency_ms": round(np.mean(self.latency_history), 1),
            "p50_latency_ms": round(np.percentile(self.latency_history, 50), 1),
            "p95_latency_ms": round(np.percentile(self.latency_history, 95), 1),
            "p99_latency_ms": round(np.percentile(self.latency_history, 99), 1),
            "total_requests": len(self.latency_history),
            "requests_under_300ms": sum(1 for l in self.latency_history if l < 300),
            "sla_compliance": round(
                sum(1 for l in self.latency_history if l < 300) / max(len(self.latency_history), 1) * 100, 1
            ),
        }
