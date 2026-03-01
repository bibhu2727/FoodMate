"""
Ranking Model (Stage 2) for CSAO Recommendation System.
LightGBM-based binary classifier that scores candidate add-ons
by probability of acceptance. Trained on historical interaction data.
"""
import os
import json
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split

from .feature_engine import (
    build_feature_vector,
    feature_dict_to_array,
    FEATURE_NAMES,
)


class RankingModel:
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.feature_names = FEATURE_NAMES

    def prepare_training_data(self, interactions, restaurants_map, users_map):
        """Convert interaction records to feature matrix + labels."""
        X_rows = []
        y = []

        for ix in interactions:
            user_id = ix["user_id"]
            rest_id = ix["restaurant_id"]
            item_id = ix["item_id"]

            user = users_map.get(user_id, {})
            rest = restaurants_map.get(rest_id, {})

            rest_menu = rest.get("menu", [])
            candidate = None
            for m in rest_menu:
                if m["item_id"] == item_id:
                    candidate = m
                    break
            if candidate is None:
                candidate = {
                    "name": ix.get("item_name", ""),
                    "category": ix.get("item_category", "mains"),
                    "base_price": 200,
                    "veg_type": "veg",
                    "popularity_score": 0.5,
                    "avg_rating": 3.5,
                    "times_ordered": 100,
                }

            cart_items = []
            for cid in ix.get("cart_items", []):
                for m in rest_menu:
                    if m["item_id"] == cid:
                        cart_items.append(m)
                        break

            context = {
                "hour": ix.get("hour", 12),
                "day_of_week": ix.get("day_of_week", 3),
                "meal_time": ix.get("meal_time", "lunch"),
                "city": ix.get("city", "Mumbai"),
            }

            fv = build_feature_vector(cart_items, candidate, context, user, rest)
            X_rows.append(feature_dict_to_array(fv))
            y.append(ix["label"])

        return np.array(X_rows), np.array(y)

    def train(self, X, y):
        """Train LightGBM ranking model."""
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        train_data = lgb.Dataset(X_train, label=y_train, feature_name=self.feature_names)
        val_data = lgb.Dataset(X_val, label=y_val, feature_name=self.feature_names, reference=train_data)

        params = {
            "objective": "binary",
            "metric": ["auc", "binary_logloss"],
            "boosting_type": "gbdt",
            "num_leaves": 63,
            "learning_rate": 0.05,
            "feature_fraction": 0.8,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
            "n_jobs": -1,
            "seed": 42,
        }

        callbacks = [lgb.log_evaluation(50), lgb.early_stopping(30)]

        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=300,
            valid_sets=[train_data, val_data],
            valid_names=["train", "val"],
            callbacks=callbacks,
        )

        self.is_trained = True
        val_preds = self.model.predict(X_val)
        return X_val, y_val, val_preds

    def predict(self, feature_vectors):
        """Predict acceptance probabilities for feature vectors."""
        if not self.is_trained:
            return np.full(len(feature_vectors), 0.5)
        return self.model.predict(feature_vectors)

    def score_candidates(self, cart_items, candidates, context, user=None, restaurant=None):
        """Score a list of candidate items and return sorted with probabilities."""
        if not candidates:
            return []

        feature_vectors = []
        for cand in candidates:
            fv = build_feature_vector(cart_items, cand, context, user, restaurant)
            feature_vectors.append(feature_dict_to_array(fv))

        X = np.array(feature_vectors)
        probabilities = self.predict(X)

        scored = []
        for cand, prob in zip(candidates, probabilities):
            scored.append({
                **cand,
                "score": round(float(prob), 4),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def save(self, path):
        if self.model:
            self.model.save_model(path)

    def load(self, path):
        if os.path.exists(path):
            self.model = lgb.Booster(model_file=path)
            self.is_trained = True
            return True
        return False

    def get_feature_importance(self):
        if not self.is_trained:
            return {}
        importance = self.model.feature_importance(importance_type="gain")
        return dict(zip(self.feature_names, [round(float(v), 2) for v in importance]))
