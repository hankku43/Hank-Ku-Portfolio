from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import digit, ptt, nn, vehicle, classical_nlp, rag

app = FastAPI(title="MyPage Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(digit.router,        prefix="/api/digit",   tags=["digit"])
app.include_router(ptt.router,          prefix="/api/ptt",     tags=["ptt"])
app.include_router(nn.router,           prefix="/api/nn",      tags=["nn"])
app.include_router(vehicle.router,      prefix="/api/vehicle", tags=["vehicle"])
app.include_router(classical_nlp.router,prefix="/api/nlp",     tags=["nlp"])
app.include_router(rag.router,          prefix="/api/rag",     tags=["rag"])


@app.get("/")
def health():
    return {"status": "ok", "message": "Portfolio API is running"}
