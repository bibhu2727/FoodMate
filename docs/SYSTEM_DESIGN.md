# CSAO Rail — System Design Document

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT (React)                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Restaurant  │  │    Menu      │  │    Cart + CSAO Rail    │  │
│  │  Selector    │  │    Grid      │  │  (Real-time updates)   │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP POST /api/recommend
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  /restaurants│  │  /recommend  │  │    /metrics            │  │
│  │  /menu       │  │  (main API)  │  │    /feature-importance │  │
│  └─────────────┘  └──────┬───────┘  └────────────────────────┘  │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                 RECOMMENDATION ENGINE                            │
│                                                                  │
│  ┌─────────────────────┐    ┌──────────────────────────────┐    │
│  │  STAGE 1:           │    │  STAGE 2:                    │    │
│  │  Candidate Generator│───▶│  LightGBM Ranker             │    │
│  │                     │    │                              │    │
│  │  • Co-occurrence    │    │  • 37 features               │    │
│  │  • Popularity       │    │  • Binary classification     │    │
│  │  • Meal patterns    │    │  • Probability scoring       │    │
│  │  • Meal-gap detect  │    │  • Cold-start fallback       │    │
│  └─────────────────────┘    └──────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  FEATURE ENGINE (37 features across 5 entities)          │    │
│  │  Cart(10) + Candidate(9) + Context(7) + User(6) + Rest(5)│   │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## 2. Two-Stage Recommendation Pipeline

### Stage 1: Candidate Generation (< 5ms)
**Goal**: Quickly narrow full menu (~20 items) to ~20 candidates

**Techniques**:
- **Item Co-occurrence Matrix**: Built from historical order data. If Biryani frequently co-occurs with Salan, Salan gets a high candidate score when Biryani is in cart.
- **Category Popularity**: Track which items are most popular within each category.
- **Meal-Time Patterns**: Different recommendations for breakfast vs dinner.
- **Meal-Gap Heuristics**: Detect missing meal components (no beverage? → boost beverages).

### Stage 2: Ranking Model (< 50ms)
**Goal**: Score and rank candidates by acceptance probability

**Model**: LightGBM binary classifier
- **Why LightGBM?**: Industry-standard for ranking. Sub-millisecond inference.
  Handles categorical features natively. Interpretable via feature importance.
- **Input**: 37-feature vector per candidate
- **Output**: P(accept | cart, context, user, restaurant)
- **Training**: Historical interaction data with temporal train-test split

### Feature Groups (37 total)

| Group | Features | Examples |
|-------|----------|---------|
| Cart Context (10) | Size, total, avg price, category presence, veg ratio, diversity | `cart_has_beverages`, `cart_category_diversity` |
| Candidate Item (9) | Price, category, veg type, popularity, rating, gap-filling | `fills_meal_gap`, `price_ratio_to_cart` |
| Temporal Context (7) | Hour, meal time, weekend, city | `is_dinner`, `is_late_night` |
| User Profile (6) | Segment, frequency, AOV, account age, diet pref, is_new | `user_segment`, `user_is_new` |
| Restaurant (5) | Rating, price tier, cuisine, chain indicator, order volume | `rest_is_chain`, `rest_cuisine` |

## 3. Sequential Cart Update Handling

**Key Innovation**: Recommendations update in real-time as cart changes.

```
Cart: [Biryani] → Recommend: [Salan, Raita, Drinks, Dessert]
Cart: [Biryani, Salan] → Recommend: [Raita, Gulab Jamun, Drinks] (Salan removed, new items appear)
Cart: [Biryani, Salan, Gulab Jamun] → Recommend: [Drinks, Papad, Buttermilk]
```

This is achieved by re-running the full pipeline on every cart mutation:
1. Frontend detects cart change → fires API request
2. Candidate generation re-evaluates with new cart state
3. Ranker scores remaining candidates with updated cart features
4. Frontend animates the updated recommendations

**Latency Budget**: < 300ms total (network + inference)

## 4. Cold Start Strategy

| Scenario | Strategy |
|----------|----------|
| **New User** | Default user features (segment=regular, avg_order=300), rely on item popularity and restaurant patterns |
| **New Restaurant** | Default restaurant features (rating=3.5, mid tier), rely on cuisine-level patterns |
| **New Item** | Use category-level popularity + basic item features (price, veg type) |

## 5. Scalability Architecture (Production)

For millions of daily requests:

1. **Model Serving**: ONNX-converted LightGBM behind Triton Inference Server
2. **Feature Store**: Redis for real-time features (user session, cart state)
3. **Candidate Cache**: Pre-computed co-occurrence matrices per restaurant, cached in Redis
4. **API Layer**: FastAPI with async handlers behind Kubernetes HPA
5. **A/B Framework**: Feature flags for model version routing

### Latency Breakdown (Target: < 300ms)

| Component | Target | Approach |
|-----------|--------|----------|
| Network/Serialization | < 50ms | Keep payloads small, gRPC for internal |
| Feature Extraction | < 20ms | Vectorized NumPy operations |
| Candidate Generation | < 10ms | Pre-built lookup tables |
| Model Inference | < 5ms | LightGBM native inference |
| Ranking/Sorting | < 5ms | In-memory sort |
| **Total** | **< 90ms** | Well within 300ms SLA |

## 6. Trade-offs & Limitations

| Decision | Trade-off |
|----------|-----------|
| LightGBM over Deep Learning | Faster inference, more interpretable, but less capacity for complex item interactions |
| Co-occurrence over Graph NN | Simple, fast, but may miss higher-order item relationships |
| Pointwise ranking | Simple to train, but doesn't optimize list-level metrics directly |
| Synthetic data | Enables full demo, but real-world patterns may differ significantly |

## 7. Future Enhancements

1. **Sequence-aware model**: Use LSTM/Transformer to model the order in which items are added
2. **Multi-objective optimization**: Balance relevance, diversity, and business value
3. **Contextual bandits**: Online learning for exploration-exploitation
4. **Graph Neural Networks**: Model item-item and user-item relationships
5. **LLM augmentation**: Use LLMs for natural language menu understanding and cross-restaurant transfer learning
