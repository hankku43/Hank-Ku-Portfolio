"""
Traffic law RAG model.
Ported from dl_assignment/second level/week-7/rag.py
Pipeline: CKIP tokenize → Doc2Vec similarity search → Ollama Gemma3 4B generation
Multi-stage fallback: direct search → synonym expansion → legal term conversion → HyDE
"""

import re
import requests
import pandas as pd
from gensim.models.doc2vec import Doc2Vec

from app.config import settings
from app.models.ckip_shared import get_ckip_drivers

# --- Lazy-loaded globals ---
_doc2vec_model: Doc2Vec | None = None
_raw_df: pd.DataFrame | None = None
_tokenizer: "_LawTokenizer | None" = None
_initialized = False


class _LawTokenizer:
    def __init__(self):
        self.ws_driver, self.pos_driver = get_ckip_drivers()
        self.stop_pos = {"Caa", "D", "DE", "Neu", "Ng", "V_2", "PARENTHESISCATEGORY"}
        self.custom_stopwords = {
            "本", "條例", "者", "處", "新臺幣", "罰鍰", "下列", "情形",
            "之", "及", "或", "其", "違反", "規定", "處罰", "其他",
            "元", "條", "項", "款", "依", "最", "前", "並",
        }

    def _filter(self, ws, pos):
        out = []
        for word, p in zip(ws, pos):
            if p in self.stop_pos:
                continue
            if word in self.custom_stopwords:
                continue
            if len(word.strip()) <= 1 and not word.isalpha() and not word.isdigit():
                continue
            if word.isdigit():
                continue
            out.append(word)
        return out

    def tokenize_query(self, text: str) -> str:
        text = re.sub(r"[\s\r\n，。；：？！、違法嗎罰]", "", text)
        ws = self.ws_driver([text], use_delim=True)
        pos = self.pos_driver(ws, use_delim=True)
        return " ".join(self._filter(ws[0], pos[0]))


# --- Core RAG helpers ---

def _call_ollama(prompt: str) -> str:
    from app.config import settings
    resp = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json={"model": "gemma3:4b", "prompt": prompt, "stream": False},
        timeout=60,
    )
    return resp.json().get("response", "")


def _clean_llm_output(text: str) -> str:
    text = re.sub(r"[A-Za-z0-9\!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?？＿]+", " ", text)
    return " ".join(text.replace("\n", " ").split())


def _rag_search(query: str, top_k: int, score_filter: float, is_first: bool):
    processed = _tokenizer.tokenize_query(query)
    query_words = processed.split()
    query_vector = _doc2vec_model.infer_vector(query_words, epochs=20)
    sims = _doc2vec_model.dv.most_similar([query_vector], topn=top_k)

    seen = set()
    results = []
    for chunk_id, score in sims:
        if score < (0.2 if is_first else score_filter):
            continue
        specific_id = chunk_id.split("_")[0]
        if specific_id in seen:
            continue
        seen.add(specific_id)
        row = _raw_df[_raw_df["specific_id"] == specific_id]
        if not row.empty:
            content = row.iloc[0]["ArticleContent"]
            results.append({
                "id": specific_id,
                "text": f"{row.iloc[0]['ArticleNo']}: {content}",
                "score": score,
            })

    if is_first:
        if not results:
            raise ValueError("查無相關法規，請嘗試更改查詢內容。")
        results = [r for r in results if r["score"] >= score_filter]

    return results, query_words


def _generate_and_check(user_query: str, search_results: list, fake_answer=None) -> str | None:
    if not search_results:
        return None
    context = "\n".join([f"分數: {r['score']:.3f}, 法規: {r['text']}" for r in search_results])
    if fake_answer:
        prompt = f"這是一則錯誤訊息：{fake_answer}。請根據以下法規更正：\n{context}\n回答原問題：{user_query}"
    else:
        prompt = f"法規內容：\n{context}\n根據上述內容回答問題：{user_query}\n若無相關資訊請回答「無法回答」。"
    response = _call_ollama(prompt)
    if "無法回答" in response or "無相關資訊" in response:
        return None
    return response


def _build_output(question: str, answer: str, search_results: list) -> dict:
    retrieved = [
        {"content": r["text"], "similarity": round(float(r["score"]), 4), "article": r["id"]}
        for r in search_results
    ]
    return {"answer": answer, "retrieved": retrieved, "question": question}


# --- Public streaming interface ---

def query_stream(question: str, top_k: int = 3):
    """Generator yielding ('status', str) then ('result', dict)."""
    global _doc2vec_model, _raw_df, _tokenizer, _initialized

    if not _initialized:
        yield "status", "首次啟動：載入 Doc2Vec 語意模型中..."
        _doc2vec_model = Doc2Vec.load(settings.rag_doc2vec_path)
        yield "status", "首次啟動：載入交通法規條文資料..."
        _raw_df = pd.read_csv(settings.rag_csv_path)
        yield "status", "首次啟動：初始化 CKIP 中文斷詞引擎（需時較長）..."
        _tokenizer = _LawTokenizer()
        _initialized = True

    yield "status", "斷詞與語意向量化中..."
    try:
        search_results, query_words = _rag_search(question, top_k, score_filter=0.8, is_first=True)
        yield "status", f"找到 {len(search_results)} 筆相關條文，呼叫 Gemma3 生成回答中..."
        response = _generate_and_check(question, search_results)
        if response:
            yield "result", _build_output(question, response, search_results)
            return
    except ValueError as e:
        yield "result", _build_output(question, f"⚠️ {e}", [])
        return

    strategies = [
        ("同義詞擴充", 0.6, lambda qw: _call_ollama(
            f"請將下列單詞分別擴充成3個法律同義詞，例如：'手機'->'行動電話 手持裝置'。單詞：{qw}。僅回傳詞彙，用空白分隔，不要有標點或說明。"
        )),
        ("法律用語轉換", 0.5, lambda qw: _call_ollama(
            f"請將此口語轉換為正式法律檢索詞，例如：'車禍'->'交通事故 碰撞'。內容：{qw}。僅回傳詞彙，不要底線、不要說明。"
        )),
        ("HyDE", 0.4, lambda qw: _call_ollama(
            f"請根據交通法規知識，簡單回答此問題：{question}。回答需包含正式法規術語。"
        )),
    ]

    for name, score, transform_fn in strategies:
        yield "status", f"策略 [{name}]：擴充查詢關鍵詞中..."
        target = question if "HyDE" in name else query_words
        raw_output = transform_fn(target)
        refined = _clean_llm_output(raw_output)
        if not refined.strip():
            continue
        new_query = f"{' '.join(query_words)} {refined}".strip()
        yield "status", f"策略 [{name}]：重新搜尋條文（閾值 {score}）..."
        search_results, _ = _rag_search(new_query, top_k, score_filter=score, is_first=False)
        yield "status", f"策略 [{name}]：呼叫 Gemma3 生成回答中..."
        is_hyde = "HyDE" in name
        response = _generate_and_check(question, search_results, fake_answer=new_query if is_hyde else None)
        if response:
            yield "result", _build_output(question, response, search_results)
            return

    yield "result", _build_output(question, "⚠️ 抱歉，目前找不到相關法規規定，請嘗試更換關鍵字查詢。", [])


# --- Backward-compat non-streaming interface ---

def query(question: str, top_k: int = 3) -> dict:
    result = None
    for event_type, data in query_stream(question, top_k):
        if event_type == "result":
            result = data
    return result
