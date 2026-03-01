"""
CSAO Recommendation System — FastAPI Entry Point.
Initializes the ML engine on startup and serves the API.
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.routes import router, set_engine
from ml.recommender import RecommendationEngine

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
engine = RecommendationEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load or train models on startup."""
    print("=" * 60)
    print("CSAO Recommendation Engine Starting...")
    print("=" * 60)

    loaded = engine.load_models(DATA_DIR)
    if not loaded:
        print("No pre-trained models found. Training from scratch...")
        train_info = engine.train(DATA_DIR)
        print(f"Training complete: {train_info}")
    else:
        print("Pre-trained models loaded successfully.")

    set_engine(engine)
    print(f"Loaded {len(engine.restaurants)} restaurants, {len(engine.users)} users")
    print("Engine ready! API is live.")
    print("=" * 60)

    yield

    print("Shutting down CSAO engine...")


app = FastAPI(
    title="CSAO Rail Recommendation System",
    description="Intelligent Cart Super Add-On recommendations for food delivery",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "CSAO Rail Recommendation System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
