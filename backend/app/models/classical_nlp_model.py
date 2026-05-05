"""
Classical Chinese language model inference.
Architecture: Character-level Transformer (Decoder-only with causal mask)
Trained on: 論語, 孟子, 中庸
"""
import json
import math
import os

import torch
import torch.nn as nn

_BASE = os.path.join(os.path.dirname(__file__), "..", "..", "models")
_DATA_PATH = os.path.join(_BASE, "classical_chinese_data.json")
_MODEL_PATH = os.path.join(_BASE, "classical_chinese_lm.pth")


# ── Model Architecture (must match training hyperparameters exactly) ──

class _CharTokenizer:
    def __init__(self, text: str):
        chars = sorted(set(text))
        self.char2idx = {ch: i for i, ch in enumerate(chars)}
        self.idx2char = {i: ch for i, ch in enumerate(chars)}
        self.vocab_size = len(chars)

    def encode(self, s: str) -> list:
        return [self.char2idx[c] for c in s if c in self.char2idx]

    def decode(self, ids: list) -> str:
        return "".join(self.idx2char[i] for i in ids)


class _PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer("pe", pe)

    def forward(self, x):
        x = x + self.pe[: x.size(0), :]
        return self.dropout(x)


class _ClassicalChineseLM(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_layers=4, dim_feedforward=512, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = _PositionalEncoding(d_model, dropout)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)

    def generate_square_subsequent_mask(self, sz: int):
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        return mask.float().masked_fill(mask == 0, float("-inf")).masked_fill(mask == 1, 0.0)

    def forward(self, src, src_mask):
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src, src_mask)
        return self.fc_out(output)


# ── Lazy Singleton ────────────────────────────────────────────────────

_model: "_ClassicalChineseLM | None" = None
_tokenizer: "_CharTokenizer | None" = None
_device: "torch.device | None" = None


def _load():
    global _model, _tokenizer, _device

    if torch.cuda.is_available():
        _device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        _device = torch.device("mps")
    else:
        _device = torch.device("cpu")

    data_path = os.path.normpath(_DATA_PATH)
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    text = "".join(p + "\n" for chapter in data for p in chapter.get("paragraphs", []))
    _tokenizer = _CharTokenizer(text)

    _model = _ClassicalChineseLM(
        vocab_size=_tokenizer.vocab_size,
        d_model=256, nhead=8, num_layers=4,
        dim_feedforward=512, dropout=0.1,
    )
    model_path = os.path.normpath(_MODEL_PATH)
    _model.load_state_dict(torch.load(model_path, map_location=_device, weights_only=True))
    _model.eval()
    _model.to(_device)


# ── Inference ─────────────────────────────────────────────────────────

def generate(prompt: str, style: str, max_length: int, temperature: float) -> dict:
    if _model is None:
        _load()

    chars = _tokenizer.encode(prompt)
    prompt_len = len(chars) # 這是輸入長度
    
    if not chars:
        chars = _tokenizer.encode("子曰：")
        prompt_len = len(chars)

    newline_id = _tokenizer.char2idx.get("\n")
    src = torch.tensor(chars, dtype=torch.long).unsqueeze(1).to(_device)

    with torch.no_grad():
        # i 從 0 到 max_length，代表「額外生成」的字數
        for i in range(max_length):
            src_mask = _model.generate_square_subsequent_mask(src.size(0)).to(_device)
            output = _model(src, src_mask)
            
            logits = output[-1, 0, :] / temperature
            
            if newline_id is not None:
                # ── 這裡就是你說的「扣除/對準」邏輯 ──
                # 既然 i 是從 0 開始，它本身就是「純輸出長度」
                # 我們讓夫子至少要說到 prompt_len 的 2 倍長度才開始有壓力
                threshold = prompt_len * 2.0
                
                # 計算 Bias：只有當 i 超過兩倍輸入長度時，bias 才會大於 0
                bias = max(0, (i - threshold)) * 0.5
                logits[newline_id] += bias
                
            prob = torch.softmax(logits, dim=0)
            next_char = torch.multinomial(prob, 1).item()
            
            chars.append(next_char)
            src = torch.tensor(chars, dtype=torch.long).unsqueeze(1).to(_device)
            
            if _tokenizer.idx2char[next_char] == "\n":
                break

    generated = _tokenizer.decode(chars)
    # 計算 tokens_generated 時也確保一致性
    return {
        "output": generated,
        "style": style,
        "tokens_generated": len(chars) - prompt_len,
    }