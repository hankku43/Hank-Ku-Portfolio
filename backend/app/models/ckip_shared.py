from functools import lru_cache
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger


@lru_cache(maxsize=1)
def get_ckip_drivers():
    print("Initializing CKIP drivers (shared)...")
    ws = CkipWordSegmenter(model="bert-base", device=-1)
    pos = CkipPosTagger(model="bert-base", device=-1)
    return ws, pos
