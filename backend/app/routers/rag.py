import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter()


class QueryRequest(BaseModel):
    prompt: str = Field(..., max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


class RetrievedDoc(BaseModel):
    content: str
    similarity: float
    article: str


class QueryResponse(BaseModel):
    answer: str
    retrieved: list[RetrievedDoc]
    question: str


@router.post("/query-stream")
async def query_traffic_law_stream(req: QueryRequest):
    from app.models.rag_model import query_stream

    def generate():
        try:
            for event_type, data in query_stream(req.prompt, req.top_k):
                if event_type == "status":
                    payload = json.dumps({"type": "status", "message": data}, ensure_ascii=False)
                else:
                    payload = json.dumps({"type": "result", **data}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
        except Exception as e:
            error = json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
            yield f"data: {error}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/query", response_model=QueryResponse)
async def query_traffic_law(req: QueryRequest):
    from app.models.rag_model import query
    try:
        return query(req.prompt, req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
