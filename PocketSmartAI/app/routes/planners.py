import json
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.orm import Session
from PIL import Image
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.db import RecommendationHistory, User
from app.models.schemas import HomeBudgetInput, PartyBudgetInput, JewelryBudgetInput
from app.services.recommendation_service import get_home_recommendations, get_party_recommendations, get_jewelry_recommendations

router = APIRouter()

async def save_upload(image: UploadFile) -> Path:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(400, "Only image uploads are allowed")
    data = await image.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Image must be <= {settings.max_upload_mb} MB")
    suffix = Path(image.filename or "outfit.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"
    target = settings.upload_path / f"{uuid4().hex}{suffix}"
    target.write_bytes(data)
    try:
        with Image.open(target) as im:
            im.verify()
    except Exception:
        target.unlink(missing_ok=True)
        raise HTTPException(400, "Invalid image file")
    return target

def save_history(db: Session, user: User, kind: str, input_data: dict, result: dict) -> None:
    db.add(RecommendationHistory(user_id=user.id, recommendation_type=kind, input_summary=json.dumps(input_data, ensure_ascii=False), result_json=json.dumps(result, ensure_ascii=False)))
    db.commit()

@router.post("/generate-home")
async def generate_home(payload: HomeBudgetInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    result = await run_in_threadpool(get_home_recommendations, payload)
    save_history(db, user, "home", payload.model_dump(), result)
    return result

@router.post("/generate-party")
async def generate_party(payload: PartyBudgetInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    result = await run_in_threadpool(get_party_recommendations, payload)
    save_history(db, user, "party", payload.model_dump(), result)
    return result

@router.post("/generate-jewelry")
async def generate_jewelry(
    total_budget: float = Form(...),
    occasion: str = Form(...),
    preferences: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    payload = JewelryBudgetInput(total_budget=total_budget, occasion=occasion, preferences=preferences)
    image_path = await save_upload(image) if image else None
    try:
        result = await run_in_threadpool(get_jewelry_recommendations, payload, image_path)
        input_data = payload.model_dump()
        input_data["image"] = image.filename if image else None
        save_history(db, user, "jewelry", input_data, result)
        return result
    finally:
        if image_path:
            image_path.unlink(missing_ok=True)

@router.get("/history")
def recommendation_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(RecommendationHistory).where(RecommendationHistory.user_id == user.id).order_by(RecommendationHistory.created_at.desc())).all()
    return {"history": [{"id": x.id, "timestamp": x.created_at.isoformat(), "type": x.recommendation_type, "input": json.loads(x.input_summary), "summary": json.loads(x.result_json)} for x in rows]}

@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.scalar(select(RecommendationHistory).where(RecommendationHistory.id == recommendation_id, RecommendationHistory.user_id == user.id))
    if not row:
        raise HTTPException(404, "Recommendation not found")
    return {"id": row.id, "timestamp": row.created_at.isoformat(), "type": row.recommendation_type, "input": json.loads(row.input_summary), "full_result": json.loads(row.result_json)}
