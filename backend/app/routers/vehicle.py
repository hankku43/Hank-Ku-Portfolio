from fastapi import APIRouter, HTTPException, UploadFile, File

router = APIRouter()

CLASSES = ["Bus", "Car", "Motorcycle", "Pickup", "Truck"]


@router.post("/detect")
async def detect_vehicles(file: UploadFile = File(...)):
    from app.models.vehicle_model import detect
    try:
        contents = await file.read()
        return detect(contents)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Model integration pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classes")
def get_classes():
    return {"classes": CLASSES}
