import os
import csv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

BOARDS = [
    "Baseball", "Boy-Girl", "C_Chat", "HatePolitics",
    "Lifeismoney", "Military", "PC_Shopping", "Stock", "Tech_Job",
]

FEEDBACK_FILE = "user_feedback_ptt.csv"


class ClassifyRequest(BaseModel):
    title: str


class BoardItem(BaseModel):
    board: str
    prob: float


class ClassifyResponse(BaseModel):
    board: str
    confidence: float
    top3: list[BoardItem]


class BatchRequest(BaseModel):
    titles: list[str]


class FeedbackInput(BaseModel):
    label: str
    article_title: str


@router.post("/classify-board", response_model=ClassifyResponse)
async def classify_board(req: ClassifyRequest):
    from app.models.ptt_model import classify
    try:
        return classify(req.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-batch")
async def classify_batch(req: BatchRequest):
    from app.models.ptt_model import classify
    results = [classify(t) for t in req.titles[:20]]
    return {"results": results}


@router.post("/feedback")
def save_feedback(data: FeedbackInput):
    try:
        file_exists = os.path.isfile(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0
        with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["Label", "Article Title"])
            if not file_exists:
                writer.writeheader()
            writer.writerow({"Label": data.label, "Article Title": data.article_title})
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="無法儲存回饋")


@router.get("/boards")
def get_boards():
    return {"boards": BOARDS}
