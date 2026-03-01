# CSAO Rail Recommendation System — Implementation Plan

## Overview
End-to-end intelligent Cart Super Add-On recommendation system for food delivery.
Fully working demo (React UI + FastAPI + ML Engine) + competition documentation.

## Architecture
```
csao-recommendation-system/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── requirements.txt
│   ├── data/                      # Generated synthetic data
│   │   └── generator.py           # Realistic synthetic data generation
│   ├── ml/
│   │   ├── feature_engine.py      # Feature engineering pipeline
│   │   ├── candidate_gen.py       # Candidate generation (Stage 1)
│   │   ├── ranker.py              # Ranking model (Stage 2)
│   │   ├── recommender.py         # Unified recommendation engine
│   │   └── evaluator.py           # Offline evaluation metrics
│   └── api/
│       ├── routes.py              # API endpoints
│       └── schemas.py             # Pydantic schemas
├── frontend/                      # React + Vite
│   ├── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── RestaurantMenu.jsx
│   │   │   ├── CartSidebar.jsx
│   │   │   ├── CSAORail.jsx       # The recommendation rail
│   │   │   ├── MenuItemCard.jsx
│   │   │   ├── Header.jsx
│   │   │   └── MetricsDashboard.jsx
│   │   └── hooks/
│   │       └── useRecommendations.js
│   └── package.json
└── docs/
    ├── SYSTEM_DESIGN.md
    ├── EVALUATION_REPORT.md
    └── BUSINESS_IMPACT.md
```

## Task Breakdown

### Phase 1: Data & ML Engine (Backend)
- [x] T1.1: Synthetic data generator (users, restaurants, menus, orders)
- [x] T1.2: Feature engineering pipeline
- [x] T1.3: Candidate generation (co-occurrence + popularity)
- [x] T1.4: Ranking model (LightGBM)
- [x] T1.5: Unified recommendation engine with sequential updates
- [x] T1.6: Offline evaluation (AUC, Precision@K, NDCG)

### Phase 2: API Layer
- [x] T2.1: FastAPI endpoints (menu, recommendations, metrics)
- [x] T2.2: Latency tracking & response optimization
- [x] T2.3: Cold start handling

### Phase 3: Frontend UI
- [x] T3.1: Modern dark theme restaurant UI
- [x] T3.2: Menu grid with item cards
- [x] T3.3: Cart sidebar with CSAO rail
- [x] T3.4: Real-time recommendation updates on cart change
- [x] T3.5: Metrics dashboard (latency, model performance)

### Phase 4: Documentation
- [x] T4.1: System design document
- [x] T4.2: Evaluation report
- [x] T4.3: Business impact analysis

## Tech Stack
- **Frontend**: React 18 + Vite, Vanilla CSS (dark glassmorphism)
- **Backend**: Python FastAPI, Uvicorn
- **ML**: scikit-learn, LightGBM, NumPy, Pandas
- **Evaluation**: AUC, Precision@K, Recall@K, NDCG
