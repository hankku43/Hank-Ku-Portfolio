import base64
import io
import logging
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageOps
from torchvision import transforms

log = logging.getLogger(__name__)

CLASSES = (
    list("0123456789")
    + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    + list("abcdefghijklmnopqrstuvwxyz")
)


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 64, 3, padding=1)
        self.bn1   = nn.BatchNorm2d(64)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.bn2   = nn.BatchNorm2d(128)
        self.conv3 = nn.Conv2d(128, 256, 3, padding=1)
        self.bn3   = nn.BatchNorm2d(256)
        self.pool  = nn.MaxPool2d(2, 2)
        self.fc1   = nn.Linear(256 * 8 * 8, 1024)
        self.fc2   = nn.Linear(1024, 62)

    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _load():
    global _model
    from app.config import settings
    path = settings.digit_model_path
    abs_path = os.path.abspath(path)
    log.info("[digit] model path (raw): %s", path)
    log.info("[digit] model path (abs):  %s", abs_path)
    log.info("[digit] file exists: %s", os.path.exists(abs_path))
    log.info("[digit] cwd: %s", os.getcwd())
    _model = Net()
    sd = torch.load(abs_path, map_location=_device)
    log.info("[digit] checkpoint keys: %s", list(sd.keys()))
    _model.load_state_dict(sd)
    _model.eval()
    _model.to(_device)
    log.info("[digit] model loaded OK, device=%s", _device)


def _square_pad_resize(img: Image.Image, target_size: int = 64, pad_color: int = 255) -> Image.Image:
    """保持長寬比縮放後，置中貼到正方形白色畫布——與訓練的 SquarePadResize 邏輯一致。"""
    w, h = img.size
    ratio = target_size / max(w, h)
    new_w, new_h = int(w * ratio), int(h * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("L", (target_size, target_size), pad_color)
    canvas.paste(img, ((target_size - new_w) // 2, (target_size - new_h) // 2))
    return canvas


_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])


def predict(image_b64: str) -> dict:
    if _model is None:
        log.info("[digit] first call — loading model...")
        _load()

    log.info("[digit] image_b64 prefix: %s", image_b64[:60])
    if "," in image_b64:
        image_b64 = image_b64.split(",")[1]
    log.info("[digit] decoded b64 length: %d chars", len(image_b64))

    raw_bytes = base64.b64decode(image_b64)
    log.info("[digit] raw PNG bytes: %d", len(raw_bytes))

    img = Image.open(io.BytesIO(raw_bytes)).convert("L")
    log.info("[digit] PIL image size: %s, mode: %s", img.size, img.mode)

    img = ImageOps.invert(img)          # 黑底白字 → 白底黑字（符合訓練資料格式）
    img = _square_pad_resize(img)       # 保持比例縮放 + 白色補邊置中 → 64x64
    tensor = _transform(img).unsqueeze(0).to(_device)
    log.info("[digit] tensor shape: %s, min=%.3f, max=%.3f", tensor.shape, tensor.min().item(), tensor.max().item())

    with torch.no_grad():
        logits = _model(tensor)
        log.info("[digit] logits shape: %s", logits.shape)
        probs = torch.softmax(logits, dim=1)[0]
        top5_idx = probs.topk(5).indices.tolist()

    result = {
        "prediction": CLASSES[top5_idx[0]],
        "confidence": round(probs[top5_idx[0]].item(), 4),
        "top5": [{"label": CLASSES[i], "prob": round(probs[i].item(), 4)} for i in top5_idx],
    }
    log.info("[digit] result: %s", result)
    return result
