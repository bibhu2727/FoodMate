# SECTION 1: TITLE PAGE

**Project Title:**  
"CSAO-AI: Real-Time Intelligent Cart Super Add-On Recommendation Engine"

**Team Name:**  
[Placeholder: Team Name]

**Hackathon:**  
Zomathon – Problem Statement 2

**Submission Date:**  
[Placeholder: Submission Date]

---

# SECTION 2: EXECUTIVE SUMMARY

**Business Problem:**  
Food delivery platforms frequently miss out on incremental revenue when users checkout without adding complementary items (beverages, desserts, side dishes). Presenting irrelevant add-ons frustrates users and leads to a poor Cart-to-Order (C2O) ratio.

**Why Cart Value Optimization Matters:**  
Optimizing the cart through intelligent, context-aware add-ons directly increases Average Order Value (AOV) and customer satisfaction without acquiring new users. It maximizes unit economics per delivery.

**Core Technical Solution:**  
We propose a two-stage sequential machine learning recommendation engine. A Candidate Generation layer quickly filters logical pairings using co-occurrence matrices and LLM embeddings, followed by a LightGBM-powered Ranking layer that scores candidates dynamically based on real-time cart contexts, user preferences, and time-of-day dynamics.

**Business Impact Potential:**  
The proposed CSAO engine is projected to deliver an 8–12% lift in AOV and a 15% increase in add-on acceptance rates by pushing hyper-relevant items at the critical checkout decision point.

**Scalability Readiness:**  
Designed with a decoupled architecture over FastAPI, decoupled feature stores, and an in-memory caching tier, the system guarantees a sub-200ms latency suitable for high-throughput, real-time production environments.

---

# SECTION 3: PROBLEM UNDERSTANDING

**Cart Context Challenges:**  
The items currently placed in the cart dramatically shift user intent. A cart with a "Spicy Chicken Burger" requires a different add-on (e.g., cooling beverage or fries) compared to a cart with just a "Salad".

**Sequential Nature of Recommendation:**  
Recommendations cannot rely on static user profiles alone; they must adapt dynamically with every item added or removed from the cart during a session.

**Contextual Relevance Issues:**  
Time of day, location, and seasonal weather heavily impact food preferences (e.g., hot coffee in the morning vs. sodas at night).

**Latency Constraint (<300ms):**  
Cart abandonment rates increase exponentially with checkout friction. Recommendations must surface instantly without blocking the checkout flow, strictly adhering to a sub-300ms latency budget.

**Cold Start Challenges:**  
New users (without order history) or new items (without co-occurrence data) must still receive relevant, logical add-on suggestions.

**Diversity & Fairness Requirement:**  
The system must promote menu diversity to prevent a "winner-takes-all" loop where only the top 3 popular items are ever recommended, ensuring fair exposure for long-tail items like specialty desserts.

---

# SECTION 4: DATA PREPARATION & FEATURE ENGINEERING (20%)

## 4.1 Synthetic Data Realism
To robustly test the engine, we engineered highly realistic synthetic datasets mirroring actual platform dynamics:
- **City-wise ordering behavior:** Distinct pricing and preference distributions across tiers.
- **Peak hours:** Pronounced volume spikes during lunch (1-3 PM) and dinner (7-9 PM).
- **Sparse user histories:** Typical power-law distribution where many users have few orders.
- **Mealtime patterns:** Strong correlations between time-of-day and category (e.g., breakfast vs. late-night snacks).
- **Restaurant diversity:** Ranging from single-cuisine local joints to diverse multi-cuisine chains.

## 4.2 Feature Categories
- **User Features:** Historical AOV, preferred cuisines, vegetarian/non-vegetarian affinity, past add-on acceptance rate.
- **Restaurant Features:** Price tier, rating, primary cuisine, popular add-ons.
- **Cart Context Features:** Current cart value, number of items, dominant cuisine in cart, sequence of additions.
- **Contextual Features:** Time of day, day of week, inferred meal type.
- **Historical Interaction Features:** User-item interaction frequency, global item co-occurrence probabilities.

## 4.3 Feature Pipeline Architecture Diagram

```text
[ Raw Data Streams ]
        │
        ▼
[ Feature Engineering ] (Aggregations, Encodings, TF-IDF)
        │
        ▼
[ Real-Time Feature Store ] (Redis / In-memory Cache)
        │
        ▼
[ Real-Time Inference Engine ]
```

**Feature Refresh Strategy:**  
Historical and user profile features are refreshed via nightly batch jobs, while session features (cart composition) are updated in real-time.

**Real-Time Feature Retrieval:**  
Low-latency NoSQL/In-memory datastores ensure instantaneous feature hydration during request time.

## 4.4 Cold Start Strategy
- **Popularity Fallback:** Presenting globally trending add-ons for the specific time-of-day.
- **Embedding Similarity:** Using item-text embeddings to map new items to similar historical counterparts.
- **Cuisine-Based Heuristics:** Defaulting to highly compatible items from the same cuisine tree if user history is absent.

---

# SECTION 5: PROBLEM FORMULATION (15%)

We formulate this as a **SEQUENTIAL RANKING** problem rather than simple multi-class classification, due to the dynamic set of available candidates and the varying context of the cart. 

**Two-Stage Architecture:** 
Using a unified architecture of Candidate Generation + Ranking optimizes for both speed and accuracy. 
- **Candidate Generation** prunes the menu of 1000s of items down to ~50 logical possibilities (O(1) lookups).
- **Ranking** applies heavy ML scoring to find the top 5 (O(N) operations).

**Constraints Handled:**
Price constraints (recommending add-ons < 30% of cart value) and hard exclusions (no non-veg add-ons for a purely veg cart) are filtered early to save computation.

📌 **Diagram – Recommendation Flow**

```text
[ User Cart Update ] (Triggers Event)
        ↓
[ Candidate Generator ] (Filters illogical/irrelevant items)
        ↓
[ Ranking Model ] (Scores candidates using LightGBM context features)
        ↓
[ Top-N Recommendations ] (Rendered on CSAO Rail)
```

---

# SECTION 6: MODEL ARCHITECTURE & AI EDGE (20%)

## 6.1 Layer 1 – Candidate Generation
Quickly surfaces a high-recall candidate pool using pre-computed item-to-item co-occurrence matrices (Association Rules) and localized restaurant popularity metrics.

## 6.2 Layer 2 – Ranking Model
A LightGBM (Gradient Boosting) scoring layer predicts the probability of an item being added to the cart. It naturally handles non-linear feature interactions (e.g., Nighttime + Heavy Cart = Dessert).
- **Feature Importance:** Highlights interactions like `cart_value` and `time_of_day` driving the highest information gain.

## 6.3 LLM Intelligence Layer (AI Edge)
To overcome sparse data, an LLM intelligence heuristic layer is integrated:
- **Menu Embedding:** `sentence-transformers` capture deep semantic relationships between food items (e.g., "Latte" and "Muffin").
- **Meal Completion Reasoning:** The model identifies syntactic logic (e.g., main + side + beverage).
- **Complement Category Detection:** Maps missing categories to the current cart context.

**Hybrid Scoring Formula:**
```
Final Score = (0.5 × ML Score) + (0.3 × Complementarity Score) + (0.2 × LLM Reasoning Score)
```

*Competitive Advantage:* This hybrid approach prevents the recommendation of repetitive items and injects "common sense" into pure statistical correlations.

---

# SECTION 7: SYSTEM ARCHITECTURE & PRODUCTION READINESS (15%)

**FULL Architecture Diagram:**

```text
[ Frontend View (React UI) ]
             ↓
[ API Gateway / Load Balancer ]
             ↓
[ CSAO FastAPI Target Service ]
             ↓
    [ Feature Store Service ] <----> [ Cached User Profiles & Embeddings ]
             ↓
    [ Candidate Engine (Stage 1) ]
             ↓
    [ Ranking Engine (Stage 2 - LightGBM) ]
             ↓
[ Context & Rules Cache / Filters ]
             ↓
[ JSON Response Top-K Items ]
```

**Production Readiness Breakdown:**
- **Latency Budget Breakdown:** Feature Hydration (20ms) + Candidate Gen (30ms) + Ranking Inference (80ms) + Overhead/Network (40ms) = ~170ms response time.
- **Caching Strategy:** Aggressive caching of item metadata and static features via Redis.
- **Horizontal Scalability:** Stateless FastAPI nodes gracefully scale behind load balancers.
- **Real-Time Serving (<200ms):** Strict adherence to SLA ensuring sub-200ms round trips.
- **Feature Store Design:** Separation of cold storage (S3/Snowflake) from hot real-time feature delivery.
- **Monitoring and logging:** Prometheus/Grafana endpoint tagging to monitor real-time model SLA and latency regressions.

---

# SECTION 8: MODEL EVALUATION & FINE-TUNING (15%)

## 8.1 Offline Evaluation
Models are validated using a temporal train-test split (testing on future unseen orders) to mimic real-world deployment.
- **AUC (Area Under ROC Curve):** Measures discrimination capability.
- **Precision@K & Recall@K:** Evaluates the relevance of the top-5 slots shown to the user.
- **NDCG (Normalized Discounted Cumulative Gain):** Rewards the system for putting the highly relevant add-ons at the very top of the rail.

## 8.2 Segment-level Error Analysis
The model's SLA is segmented to ensure equitable performance:
- **Budget Users vs Premium Users:** Ensuring add-on price points match purchasing power thresholds.
- **Lunch vs Dinner:** Tuning time-decay weights if midday snack recommendations bleed into dinner entrées.

## 8.3 Optimization Strategy
- **Hyperparameter Tuning:** Bayesian optimization on LightGBM tree-depth, learning rates, and L1/L2 regularization.
- **Accuracy vs Latency Tradeoff:** Dynamic restriction of candidate pool sizes during high load to guarantee P99 latency remains consistent.

---

# SECTION 9: BUSINESS IMPACT & A/B TESTING DESIGN (15%)

## 9.1 Metric Translation
By increasing the precision of the top recommendations (Higher Precision@K), users experience less friction and find exactly what they desire. This leads to a **Higher Add-on Acceptance Rate**, which directly multiplies the **Average Order Value (AOV)** across millions of transactions.

## 9.2 A/B Testing Plan
**Control (A):** Random or generic popularity-based static add-ons.
**Treatment (B):** Real-time Context-Aware CSAO Engine.

**Success Metrics:**
- **AOV Lift:** Net increase in cart value per transaction.
- **CSAO Attach Rate:** Percentage of orders completed with at least one suggested add-on.
- **C2O Ratio:** Cart-to-Order conversion rate improvement.

**Guardrail Metrics:**
- **Cart Abandonment:** Ensuring the feature doesn't cause decision paralysis or drop-offs.
- **Latency:** Must remain structurally unharmed compared to Control.

## 9.3 Projected Impact
Based on baseline delivery market benchmarks, implementing this system conservatively projects:
- **8–12% AOV Lift** via seamless cross-selling.
- **15% Add-on Acceptance Increase** due to hyper-relevant contextual suggestions.
- **<200ms Median Latency**, preserving the smooth checkout experience.

---

# SECTION 10: TRADE-OFFS & LIMITATIONS

- **Synthetic Data Limitations:** Although structurally robust, synthetic behavior patterns lack the chaotic, unpredictable noise of live human traffic.
- **Cold Start Imperfections:** Heuristics can sometimes fail for highly specialized niche items without prior history, leaning too heavily on generic favorites.
- **Model Drift Risks:** Consumer trends change rapidly (e.g., viral food trends or seasonal anomalies), necessitating frequent model retraining pipelines to prevent degradation.

---

# SECTION 11: FUTURE IMPROVEMENTS

- **Graph Neural Networks (GNN):** Representing items, categories, and users as a bipartite graph to capture deeper, intrinsic relationships.
- **Reinforcement Learning (RL) / Multi-armed Bandits:** Training the ranker dynamically to balance exploration (new menu items) vs. exploitation (known best-sellers).
- **Deep Session Modeling:** Adopting Transformer-based sequences (like BERT4Rec) to attend to the entire lifecycle and hesitations within a user’s checkout timeline.
- **Continuous Learning Pipeline:** Enabling online learning to adapt the LightGBM trees continuously on live traffic, minimizing manual retraining ops.

---

# SECTION 12: PUBLIC LINKS 

- **GitHub Repository Link:** [https://github.com/bibhu2727/FoodMate.git](https://github.com/bibhu2727/FoodMate.git)
- **Google Drive Dataset Link:** [Placeholder: Drive Link]
- **Notebook Link:** [Placeholder: Colab / Kaggle Link]
- **Live Demo Link:** [Placeholder: Vercel / Render Link]
