"""API routes for CSAO Recommendation System."""
from fastapi import APIRouter, HTTPException
from .schemas import RecommendationRequest, RecommendationResponse

router = APIRouter()

engine = None


def set_engine(e):
    global engine
    engine = e


@router.get("/restaurants")
def list_restaurants():
    if not engine or not engine.restaurants:
        raise HTTPException(status_code=503, detail="Engine not loaded")
    rests = []
    for r in engine.restaurants.values():
        rests.append({
            "restaurant_id": r["restaurant_id"],
            "name": r["name"],
            "city": r["city"],
            "cuisine_type": r["cuisine_type"],
            "price_tier": r["price_tier"],
            "rating": r["rating"],
            "avg_delivery_time": r.get("avg_delivery_time", 30),
            "is_chain": r.get("is_chain", False),
            "total_orders": r.get("total_orders", 0),
            "menu_size": len(r.get("menu", [])),
        })
    rests.sort(key=lambda x: x["rating"], reverse=True)
    return {"restaurants": rests}


@router.get("/restaurants/{restaurant_id}/menu")
def get_menu(restaurant_id: str):
    if not engine or restaurant_id not in engine.restaurants:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    rest = engine.restaurants[restaurant_id]
    return {
        "restaurant_id": restaurant_id,
        "name": rest["name"],
        "cuisine_type": rest["cuisine_type"],
        "city": rest["city"],
        "rating": rest["rating"],
        "price_tier": rest["price_tier"],
        "menu": rest.get("menu", []),
    }


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not loaded")

    cart_dicts = [item.model_dump() for item in req.cart_items]

    context = {}
    if req.hour is not None:
        context["hour"] = req.hour
    if req.meal_time:
        context["meal_time"] = req.meal_time
    if req.city:
        context["city"] = req.city

    result = engine.recommend(
        restaurant_id=req.restaurant_id,
        cart_items=cart_dicts,
        context=context if context else None,
        user_id=req.user_id,
        top_n=req.top_n,
    )
    return result


@router.get("/metrics")
def get_metrics():
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not loaded")
    return engine.get_metrics()


@router.get("/feature-importance")
def get_feature_importance():
    if not engine or not engine.ranker.is_trained:
        raise HTTPException(status_code=503, detail="Model not trained")
    return engine.ranker.get_feature_importance()
