from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ForwardRequest(BaseModel):
    inputs: list[float]


class LayerActivation(BaseModel):
    layer: int
    values: list[float]
    activation: str


class ForwardResponse(BaseModel):
    output: list[float]
    prediction: int
    layers: list[LayerActivation]
    loss: float


@router.post("/forward", response_model=ForwardResponse)
async def forward_pass(req: ForwardRequest):
    from app.models.nn_model import forward
    try:
        return forward(req.inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/architecture")
def get_architecture():
    return {
        "layers": [2, 4, 4, 1],
        "activations": ["relu", "relu", "sigmoid"],
        "task": "XOR",
        "description": "手刻 XOR 神經網路，純 Python 實作無框架依賴",
    }
