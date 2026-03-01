# 🍽️ FoodMate: CSAO Rail Recommendation System

An intelligent, end-to-end **Cart Super Add-On (CSAO)** recommendation system for food delivery platforms. This project features a stunning React frontend with glassmorphic aesthetics and a FastAPI backend powered by Machine Learning (LightGBM) to deliver real-time, context-aware add-on recommendations based on user cart contents.

---

## 🚀 Features

- **Real-Time ML Recommendations**: Context-aware cart add-on suggestions updated dynamically as users build their orders.
- **Glassmorphic UI**: Beautiful, premium dark-themed React UI inspired by modern design trends.
- **Interactive Checkout Flow**: Seamless checkout experience with simulated payment processing and success animations.
- **Metrics Dashboard**: Live tracking of recommendation latency and model performance.
- **Performance Optimized**: Low-latency backend inference via Python FastAPI.

---

## 🛠️ Tech Stack

### Frontend (User Interface)
- **Framework**: React 18 + Vite
- **Styling**: Vanilla CSS (Custom modern dark theme, CSS Variables, Glassmorphism)
- **Components**: Component-based architecture with interactive cart sidebars and checkout views

### Backend (ML Engine & API)
- **Framework**: Python FastAPI, Uvicorn (ASGI Server)
- **Machine Learning**: LightGBM (Gradient Boosting Framework), Scikit-Learn, Pandas, NumPy
- **Architecture**: Multi-stage Recommendation Engine (Candidate Generation -> Ranking)
- **Data**: Synthetic real-world dataset generation (Users, Restaurants, Menus, Orders)

---

## 📦 Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- Python (3.9+ recommended)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/bibhu2727/FoodMate.git
cd FoodMate
```

### 2. Start the Backend (FastAPI + ML Engine)
The backend requires creating the synthetic data and training the ML model upon first launch.

```bash
cd backend
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m uvicorn main:app --reload --port 8000
```
> Note: On initial startup, the engine will automatically generate data and train the `LightGBM` model. You'll see `Engine ready! API is live.` in the console when it's done.

### 3. Start the Frontend (React + Vite)
Open a **new terminal tab/window**:

```bash
cd frontend
# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

Your app will be running at: `http://localhost:5173`

---

## 🧠 Recommendation Engine Architecture

The CSAO (Cart Super Add-On) engine works in two stages:
1. **Candidate Generation**: Filters the menu to suggest logical pairings based on the user's current cart and historical co-occurrences.
2. **Ranking**: Uses a trained **LightGBM** ranker to score candidates based on contextual features (e.g., user preferences, current cart composition, price affinity, time of day).

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/bibhu2727/FoodMate/issues).

## 📄 License
This project is licensed under the MIT License.
