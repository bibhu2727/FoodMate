"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel
from typing import Optional


class CartItem(BaseModel):
    item_id: str = ""
    name: str
    category: str = "mains"
    price: float = 0
    base_price: float = 0
    veg_type: str = "veg"
    popularity_score: float = 0.5
    avg_rating: float = 3.5
    times_ordered: int = 100


class RecommendationRequest(BaseModel):
    restaurant_id: str
    cart_items: list[CartItem]
    user_id: Optional[str] = None
    hour: Optional[int] = None
    meal_time: Optional[str] = None
    city: Optional[str] = None
    top_n: int = 10


class RecommendationItem(BaseModel):
    item_id: str = ""
    name: str
    category: str
    base_price: float = 0
    price: float = 0
    veg_type: str = "veg"
    score: float = 0.0
    popularity_score: float = 0.5
    avg_rating: float = 3.5


class RecommendationResponse(BaseModel):
    recommendations: list[dict]
    latency_ms: float
    cart_size: int
    candidates_evaluated: int
    model_version: str
