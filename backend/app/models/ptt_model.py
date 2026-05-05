from functools import lru_cache

import torch
import torch.nn as nn

BOARDS = [
    "Baseball", "Boy-Girl", "C_Chat", "HatePolitics",
    "Lifeismoney", "Military", "PC_Shopping", "Stock", "Tech_Job",
]

_SKIP_POS = {"P", "Nh", "SHI", "Dfa", "PARENTHESISCATEGORY", "COLONCATEGORY", "PAUSECATEGORY"}


class PTTClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(300, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 9),
        )

    def forward(self, x):
        return self.net(x)


@lru_cache(maxsize=1)
def load_models():
    from gensim.models.doc2vec import Doc2Vec
    from app.config import settings
    from app.models.ckip_shared import get_ckip_drivers

    ws_driver, pos_driver = get_ckip_drivers()

    print("Loading Doc2Vec model...")
    doc2vec = Doc2Vec.load(settings.ptt_doc2vec_path)

    print("Loading PTT Classifier...")
    classifier = PTTClassifier()
    classifier.load_state_dict(torch.load(settings.ptt_model_path, map_location="cpu"))
    classifier.eval()

    return ws_driver, pos_driver, doc2vec, classifier


def _filter_words(sentence_ws, sentence_pos) -> list:
    res = []
    for word, p in zip(sentence_ws, sentence_pos):
        if p == "WHITESPACE" or not word.strip():
            continue
        if p in _SKIP_POS or p.startswith("C"):
            continue
        res.append(word)
    return res


def classify(title: str) -> dict:
    ws_driver, pos_driver, doc2vec, classifier = load_models()

    ws  = ws_driver([title], use_delim=True)
    pos = pos_driver(ws, use_delim=True)
    words = _filter_words(ws[0], pos[0])

    vec    = doc2vec.infer_vector(words, epochs=20)
    tensor = torch.tensor(vec, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        probs = torch.softmax(classifier(tensor), dim=1)[0]
        top3  = probs.topk(3).indices.tolist()

    return {
        "board":      BOARDS[top3[0]],
        "confidence": round(probs[top3[0]].item(), 4),
        "top3":       [{"board": BOARDS[i], "prob": round(probs[i].item(), 4)} for i in top3],
    }
