import os
import csv
from datetime import date
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated

router = APIRouter()

BOARDS = [
    "Baseball", "Boy-Girl", "C_Chat", "HatePolitics",
    "Lifeismoney", "Military", "PC_Shopping", "Stock", "Tech_Job",
]

FEEDBACK_FILE = "user_feedback_ptt.csv"
DAILY_FEEDBACK_LIMIT = 200


def _prepare_feedback_file():
    """若檔案是昨天或更早的就清空，回傳目前筆數。"""
    if os.path.isfile(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0:
        last_modified = date.fromtimestamp(os.path.getmtime(FEEDBACK_FILE))
        if last_modified < date.today():
            open(FEEDBACK_FILE, "w").close()
            return 0
        with open(FEEDBACK_FILE, encoding="utf-8-sig") as f:
            return max(0, sum(1 for _ in f) - 1)  # 扣掉 header
    return 0


class ClassifyRequest(BaseModel):
    title: str = Field(..., max_length=200)


class BoardItem(BaseModel):
    board: str
    prob: float


class ClassifyResponse(BaseModel):
    board: str
    confidence: float
    top3: list[BoardItem]


class BatchRequest(BaseModel):
    titles: list[Annotated[str, Field(max_length=200)]] = Field(..., max_length=20)


class FeedbackInput(BaseModel):
    label: str = Field(..., max_length=50)
    article_title: str = Field(..., max_length=200)


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
    if data.label not in BOARDS:
        raise HTTPException(status_code=400, detail="無效的版面名稱")
    try:
        row_count = _prepare_feedback_file()
        if row_count >= DAILY_FEEDBACK_LIMIT:
            raise HTTPException(status_code=429, detail="今日回饋已達上限，明天再試")
        file_exists = os.path.isfile(FEEDBACK_FILE) and os.path.getsize(FEEDBACK_FILE) > 0
        with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["Label", "Article Title"])
            if not file_exists:
                writer.writeheader()
            writer.writerow({"Label": data.label, "Article Title": data.article_title})
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="無法儲存回饋")


@router.get("/boards")
def get_boards():
    return {"boards": BOARDS}
