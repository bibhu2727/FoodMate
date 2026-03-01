"""
Offline Evaluation for CSAO Recommendation System.
Computes AUC, Precision@K, Recall@K, NDCG@K on held-out test data.
"""
import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score


def compute_auc(y_true, y_pred):
    """Area Under ROC Curve."""
    if len(set(y_true)) < 2:
        return 0.0
    return round(float(roc_auc_score(y_true, y_pred)), 4)


def precision_at_k(y_true, y_pred, k=5):
    """Precision@K: fraction of top-K predictions that are relevant."""
    top_k_idx = np.argsort(y_pred)[-k:]
    relevant = sum(y_true[i] for i in top_k_idx)
    return round(relevant / k, 4)


def recall_at_k(y_true, y_pred, k=5):
    """Recall@K: fraction of relevant items found in top-K."""
    total_relevant = sum(y_true)
    if total_relevant == 0:
        return 0.0
    top_k_idx = np.argsort(y_pred)[-k:]
    found = sum(y_true[i] for i in top_k_idx)
    return round(found / total_relevant, 4)


def dcg_at_k(relevances, k):
    """Discounted Cumulative Gain at K."""
    relevances = np.array(relevances[:k])
    if len(relevances) == 0:
        return 0.0
    discounts = np.log2(np.arange(2, len(relevances) + 2))
    return float(np.sum(relevances / discounts))


def ndcg_at_k(y_true, y_pred, k=5):
    """Normalized Discounted Cumulative Gain at K."""
    order = np.argsort(y_pred)[::-1]
    y_true_sorted = np.array(y_true)[order]
    dcg = dcg_at_k(y_true_sorted, k)

    ideal_order = np.argsort(y_true)[::-1]
    y_ideal = np.array(y_true)[ideal_order]
    idcg = dcg_at_k(y_ideal, k)

    if idcg == 0:
        return 0.0
    return round(dcg / idcg, 4)


def evaluate_model(y_true, y_pred, k_values=None):
    """Full evaluation suite."""
    if k_values is None:
        k_values = [3, 5, 10]

    results = {
        "auc": compute_auc(y_true, y_pred),
        "total_samples": len(y_true),
        "positive_ratio": round(float(np.mean(y_true)), 4),
    }

    for k in k_values:
        if k <= len(y_true):
            results[f"precision_at_{k}"] = precision_at_k(y_true, y_pred, k)
            results[f"recall_at_{k}"] = recall_at_k(y_true, y_pred, k)
            results[f"ndcg_at_{k}"] = ndcg_at_k(y_true, y_pred, k)

    return results


def segment_evaluation(y_true, y_pred, segments, k=5):
    """Evaluate per-segment performance."""
    unique_segments = set(segments)
    results = {}

    for seg in unique_segments:
        mask = [s == seg for s in segments]
        y_t = np.array(y_true)[mask]
        y_p = np.array(y_pred)[mask]

        if len(y_t) < 2 or len(set(y_t)) < 2:
            continue

        results[seg] = {
            "auc": compute_auc(y_t, y_p),
            "precision_at_k": precision_at_k(y_t, y_p, min(k, len(y_t))),
            "ndcg_at_k": ndcg_at_k(y_t, y_p, min(k, len(y_t))),
            "count": int(sum(mask)),
        }

    return results
