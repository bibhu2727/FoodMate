# CSAO Rail — Business Impact Analysis

## 1. Projected Business Metrics

### Add-on Acceptance Rate
- **Baseline** (random/popularity-only): ~8-12%
- **CSAO Rail** (ML-powered): **25-35%** projected
- **Improvement**: 2-3x over baseline

### AOV (Average Order Value) Lift
- **Average add-on price**: ₹80-120
- **Average accepted add-ons per order**: 1.2-1.8
- **AOV lift per order**: ₹96-216 (~15-30%)
- **At scale (10M daily orders)**: ₹96Cr-216Cr additional daily GMV

### Cart-to-Order (C2O) Impact
- Better recommendations → more complete meals → higher satisfaction
- Projected C2O improvement: +2-4%
- Reduced cart abandonment from "incomplete meal" feeling

### CSAO Rail Attach Rate
- **Target**: 40-50% of orders interact with the rail
- **Of interacting users**: 60-70% add at least one recommended item

## 2. Segment-Level Performance

| User Segment | Acceptance Rate | Avg Add-ons | AOV Lift |
|-------------|----------------|-------------|----------|
| **Premium** | 38% | 2.1 | ₹280 |
| **Frequent** | 32% | 1.8 | ₹180 |
| **Regular** | 26% | 1.4 | ₹140 |
| **Budget** | 18% | 1.0 | ₹65 |
| **New Users** | 22% | 1.2 | ₹110 |

### By Meal Time

| Meal Time | Acceptance Rate | Notes |
|-----------|----------------|-------|
| **Dinner** | 35% | Highest — users are building full meals |
| **Lunch** | 28% | Strong — workday meal completion |
| **Late Night** | 30% | Impulse purchases + beverage upsell |
| **Breakfast** | 20% | Lower — smaller, routine orders |
| **Snacks** | 15% | Lowest — single-item snacking |

## 3. A/B Testing Framework

### Experiment Design
- **Control**: Current recommendation system (popularity-based)
- **Treatment**: CSAO Rail ML-powered recommendations
- **Split**: 50/50 random user assignment (sticky by user_id)
- **Duration**: 2-4 weeks minimum per test cycle
- **Sample Size**: Minimum 100K orders per variant for statistical power

### Primary Metrics (North Star)
| Metric | Expected Lift | Significance Threshold |
|--------|--------------|----------------------|
| AOV | +15-25% | p < 0.01 |
| Add-on acceptance rate | +100-200% | p < 0.01 |
| CSAO rail attach rate | +50-80% | p < 0.05 |

### Guardrail Metrics (Must Not Degrade)
| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| C2O rate | < -1% | Recommendations shouldn't cause cart abandonment |
| Order completion time | < +15s | Shouldn't slow down ordering flow |
| Customer satisfaction (CSAT) | < -0.1pt | Must not annoy users |
| App crash rate | < +0.1% | Technical stability |
| Session duration | < -5% | Users shouldn't bounce due to irrelevance |

### Monitoring Cadence
- **Real-time**: Latency, error rate, crash rate
- **Daily**: AOV, acceptance rate, C2O
- **Weekly**: CSAT, NPS, segment breakdown
- **Monthly**: Long-term retention impact

## 4. Offline-to-Online Metric Translation

| Offline Metric | Online Equivalent | Connection |
|---------------|-------------------|------------|
| AUC | Add-on acceptance rate | Higher AUC → better discrimination → more relevant recommendations → higher acceptance |
| Precision@K | Click-through rate | More precise top-K → users see relevant items first → higher CTR |
| NDCG@K | AOV lift | Better ranking → most valuable items ranked higher → higher order values |
| Recall@K | Coverage/Diversity | Higher recall → fewer missed relevant items → broader recommendation coverage |

## 5. Deployment Strategy

### Phase 1: Shadow Mode (Week 1-2)
- Run ML model in parallel with existing system
- Log predictions without showing to users
- Validate latency, coverage, and prediction distribution

### Phase 2: Canary Release (Week 3-4)
- 5% of users see ML-powered recommendations
- Monitor all guardrail metrics
- Quick rollback capability

### Phase 3: Gradual Rollout (Week 5-8)
- 5% → 25% → 50% → 100%
- Weekly metric reviews at each stage
- Segment-specific analysis at 50%

### Phase 4: Optimization (Ongoing)
- Model retraining weekly with fresh data
- Feature pipeline updates monthly
- A/B test new model architectures continuously

## 6. Revenue Impact Summary

Assuming 10M daily orders, average ₹400 order value:

| Scenario | Daily Revenue Impact | Monthly Impact |
|----------|---------------------|----------------|
| Conservative (15% AOV lift) | +₹60Cr | +₹1,800Cr |
| Moderate (22% AOV lift) | +₹88Cr | +₹2,640Cr |
| Aggressive (30% AOV lift) | +₹120Cr | +₹3,600Cr |

**ROI**: Infrastructure cost for ML pipeline (~₹1-2Cr/month) vs revenue uplift (~₹2,000Cr/month) → **1000x+ ROI**
