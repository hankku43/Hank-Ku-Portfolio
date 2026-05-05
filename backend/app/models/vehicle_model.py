"""
Vehicle detection using Faster R-CNN ResNet50-FPN.
Model: vehicle_detection_model_5.pth
Classes: background(0), Bus(1), Car(2), Motorcycle(3), Pickup(4), Truck(5)
"""

import io
import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.rpn import AnchorGenerator
import torchvision.transforms.functional as TF
from PIL import Image

CLASSES = ["Bus", "Car", "Motorcycle", "Pickup", "Truck"]
CLASS_COLORS = {
    "Bus":        "#f59e0b",
    "Car":        "#ef4444",
    "Motorcycle": "#8b5cf6",
    "Pickup":     "#10b981",
    "Truck":      "#3b82f6",
}
NUM_CLASSES = 6  # background + 5 vehicle types
SCORE_THRESHOLD = 0.5

_model = None
_device = None


def _build_model():
    anchor_generator = AnchorGenerator(
        sizes=((8, 16, 32, 64, 128, 256),),
        aspect_ratios=((0.5, 1.0, 2.0, 3.0),),
    )
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
        weights=None,
        weights_backbone=None,
        min_size=1200,
        max_size=1333,
        anchor_generator=anchor_generator,
    )
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, NUM_CLASSES)
    return model


def _load_model():
    global _model, _device
    if _model is not None:
        return _model, _device

    from app.config import settings
    model_path = settings.vehicle_model_path

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _model = _build_model()
    _model.load_state_dict(torch.load(model_path, map_location=_device, weights_only=True))
    _model.to(_device)
    _model.eval()
    return _model, _device


def detect(image_bytes: bytes) -> dict:
    model, device = _load_model()

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = img.size

    img_tensor = TF.to_tensor(img).to(device)

    with torch.no_grad():
        outputs = model([img_tensor])[0]

    boxes = outputs["boxes"].cpu().numpy()
    labels = outputs["labels"].cpu().numpy()
    scores = outputs["scores"].cpu().numpy()

    detections = []
    for box, label, score in zip(boxes, labels, scores):
        if score < SCORE_THRESHOLD:
            continue
        label_name = CLASSES[label - 1] if 1 <= label <= len(CLASSES) else "Unknown"
        detections.append({
            "label": label_name,
            "score": float(score),
            "box": [float(x) for x in box],  # [x1, y1, x2, y2]
            "color": CLASS_COLORS.get(label_name, "#64748b"),
        })

    return {
        "detections": detections,
        "image_width": width,
        "image_height": height,
    }
