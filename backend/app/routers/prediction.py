"""
48小时指数预测 API 路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import get_db, IndexPrediction
from ..services.prediction_service import get_predictions, generate_all_predictions
from ..scrapers import INDEX_MAPPING

router = APIRouter(prefix="/prediction", tags=["prediction"])


@router.get("")
async def get_all_predictions(db: Session = Depends(get_db)):
    """
    获取所有指数的48小时预测
    """
    predictions = get_predictions(db)

    return {
        "updated_at": datetime.now().isoformat(),
        "count": len(predictions),
        "data": predictions,
    }


@router.get("/{index_code}")
async def get_index_prediction(
    index_code: str,
    db: Session = Depends(get_db),
):
    """
    获取单个指数的48小时预测
    """
    if index_code not in INDEX_MAPPING:
        return {"error": f"不支持的指数: {index_code}"}

    now = datetime.utcnow()
    record = db.query(IndexPrediction).filter(
        IndexPrediction.index_code == index_code,
        IndexPrediction.expires_at > now,
    ).order_by(IndexPrediction.predicted_at.desc()).first()

    if record:
        return {
            "updated_at": datetime.now().isoformat(),
            "data": record.to_dict(),
        }

    return {"error": "暂无预测数据", "data": None}


@router.post("/refresh")
async def refresh_predictions(db: Session = Depends(get_db)):
    """
    手动刷新所有预测（用于测试）
    """
    try:
        predictions = generate_all_predictions(db)
        return {
            "status": "success",
            "count": len(predictions),
            "data": predictions,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
