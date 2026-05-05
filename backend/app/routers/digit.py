import logging
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

log = logging.getLogger(__name__)

router = APIRouter()


class PredictRequest(BaseModel):
    image: str  # base64-encoded PNG/JPEG from Canvas


class ClassItem(BaseModel):
    label: str
    prob: float


class PredictResponse(BaseModel):
    prediction: str
    confidence: float
    top5: list[ClassItem]


@router.post("/predict", response_model=PredictResponse)
async def predict_character(req: PredictRequest):
    from app.models.digit_model import predict
    try:
        return predict(req.image)
    except Exception as e:
        tb = traceback.format_exc()
        log.error("[digit] predict failed:\n%s", tb)
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


@router.get("/classes")
def get_classes():
    classes = (
        list("0123456789")
        + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        + list("abcdefghijklmnopqrstuvwxyz")
    )
    return {"classes": classes, "count": len(classes)}
