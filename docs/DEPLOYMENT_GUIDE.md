# CSAO-AI Deployment Guide

This guide provides step-by-step instructions to deploy the CSAO Recommendation System on free-tier platforms: **Render** for the FastAPI backend and **Vercel** for the React (Vite) frontend.

---

## PART 1 — PREPARE REPOSITORY FOR DEPLOYMENT

The repository has been structured exactly for deployment. The following files have already been created for you:
- `backend/requirements.txt`: Contains all production packages (FastAPI, Uvicorn, LightGBM, Pandas, etc.)
- `backend/Procfile`: Instructs Render how to start the web server (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`)
- `backend/runtime.txt`: Enforces `python-3.11.8` during the cloud build.
- `backend/Dockerfile`: An optional containerized environment.
- `frontend/.env.example`: Demonstrates how to pass the live API URL to your Vite frontend.
- `frontend/src/App.jsx`: Updated to automatically use `import.meta.env.VITE_API_URL` when deployed.
- `backend/main.py`: CORS is actively configured to accept `allow_origins=["*"]`, allowing the frontend to connect securely.

---

## PART 2 — DEPLOY BACKEND (Render – FREE)

Render provides a completely free tier to run Python APIs. 

**Steps:**
1. Go to [https://render.com](https://render.com) and create a free account.
2. Click **New +** in the top right corner and select **Web Service**.
3. **Connect your GitHub account** and select your `FoodMate` repository.
4. On the configuration page, fill in the following details:
   - **Name:** `csao-backend` (or similar)
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000` 
   - **Instance Type:** Select the **Free** tier.
5. Click **Create Web Service**. 

Wait 2-4 minutes while Render installs your requirements. Once finished, you will see a green **"Live"** indicator. 
- **Your Backend Live URL will look like:** `https://csao-backend-xxxxx.onrender.com`

---

## PART 3 — DEPLOY FRONTEND (Vercel – FREE)

Vercel provides lightning-fast free hosting for React/Vite applications.

**Steps:**
1. Go to [https://vercel.com](https://vercel.com) and log in with your GitHub account.
2. From the dashboard, click **Add New...** > **Project**.
3. Import your `FoodMate` GitHub repository.
4. On the configuration page, set up the following:
   - **Framework Preset:** Vite (should auto-detect)
   - **Root Directory:** Edit this and type `frontend`
   - **Build Command:** `npm run build` (auto-detected)
   - **Output Directory:** `dist` (auto-detected)
5. **CRITICAL STEP:** Open the **Environment Variables** dropdown.
   - **Name:** `VITE_API_URL`
   - **Value:** `https://your-backend.onrender.com/api` *(Replace this with the actual URL Render just gave you! Make sure it ends in `/api`)*
   - Click **Add**.
6. Click **Deploy**.

Vercel will build the React code and give you your live URL in under 1 minute!
- **Your Frontend Live URL will look like:** `https://foodmate-frontend.vercel.app`

---

## PART 4 — CONNECT FRONTEND TO BACKEND

The connection happens automatically if you set `VITE_API_URL` in Vercel. 

**How it works under the hood (App.jsx):**
```javascript
// This checks Vercel's environment variables first, falling back to localhost if running on your machine.
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Example Fetch Call triggered by React:
const loadRestaurants = async () => {
    const res = await fetch(`${API_BASE}/restaurants`);
    const data = await res.json();
};
```

**CORS Handling:**
CORS errors happen when a browser blocks frontend code (Vercel URL) from talking to a different backend server (Render URL). We fixed this in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any Vercel URL to safely fetch data
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Testing the Endpoint manually:**
You can open a browser tab to `https://your-backend.onrender.com/api/restaurants` to verify it returns JSON data.

---

## PART 5 — VERIFY DEPLOYMENT

Before submitting, run these final checks:
1. **Test backend URL:** Open `https://your-backend.onrender.com/docs`. It should show the FastAPI "Swagger UI" dashboard displaying all endpoints.
2. **Test recommendation via Postman:**
   - Method: `POST`
   - URL: `https://your-backend.onrender.com/api/recommendations`
   - Body (JSON): `{"restaurant_id": "r001", "cart_items": [{"item_id": "m001"}], "context": {"city": "Mumbai"}}`
3. **Test frontend cart:** Open your Vercel URL, click a restaurant, add an item to the cart, and observe the "Recommended Add-ons" Rail populating. 
4. **Check latency:** Look at the small `⚡ 120ms` indicator on the CSAO Rail UI. It should remain below 300ms.

---

## PART 6 — OPTIONAL AUTO DOCKER DEPLOYMENT

If you prefer to deploy to platforms like AWS, Fly.io, or DigitalOcean, a complete `backend/Dockerfile` has been provided for you. 

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=10000
EXPOSE ${PORT}
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
```
To deploy using this, simply tell Render or Fly.io that you want a **Docker Build** instead of Python natively.

---

## PART 7 — COMMON ERRORS & FIXES

### 1. CORS Errors (Blocked by Origin)
**Symptom:** In the browser console (F12) you see "Access to fetch at 'X' from origin 'Y' has been blocked by CORS policy."
**Fix:** Ensure `backend/main.py` has `allow_origins=["*"]`. (Already configured).

### 2. Frontend Build Failures
**Symptom:** Vercel deployment fails on the "Build" step.
**Fix:** Check if you successfully bypassed ESLint warnings. If you ever get an error, run `npm run lint` locally, fix warnings, and commit to GitHub. Vercel will rebuild automatically.

### 3. 502 Bad Gateway / Application Error on Render
**Symptom:** Clicking the Render URL shows a white page saying "Bad Gateway" or "Application dropping connections".
**Fix:** 
- Render requires web servers to listen on specifically assigned ports. 
- Ensure your Start Command in Render uses `--port $PORT` or `--port 10000`.
- Do NOT hardcode `--port 8000` on the cloud unless specified by the provider.

### 4. Environment Variable Mistakes
**Symptom:** The frontend says "Cannot connect to backend" even though Render is live.
**Fix:** 
- Go to Vercel Settings -> Environment Variables. 
- Ensure you used `VITE_API_URL` (React/Vite specifically requires `VITE_` as a prefix for public variables).
- Make sure the URL does **not** end with a trailing slash! Add `/api` exactly. (e.g. `https://csao-backend.onrender.com/api`)
