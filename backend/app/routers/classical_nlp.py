from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    style: str = "wuyan"  # wuyan (五言絕句) | qiyan (七言絕句) | translate
    max_length: int = 100
    temperature: float = 0.85


class GenerateResponse(BaseModel):
    output: str
    style: str
    tokens_generated: int


@router.post("/generate", response_model=GenerateResponse)
async def generate_classical(req: GenerateRequest):
    from app.models.classical_nlp_model import generate
    try:
        return generate(req.prompt, req.style, req.max_length, req.temperature)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Model integration pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
