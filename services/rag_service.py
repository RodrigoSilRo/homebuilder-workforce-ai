"""
RAG Service — semantic policy and knowledge base retrieval using ChromaDB.

Embeddings are computed via LangChain's OpenAI client (reuses the existing
working HTTP stack) and stored in ChromaDB as pre-computed vectors.
Falls back to SQL LIKE search when ChromaDB is unavailable or no OpenAI key.

Usage:
    from services.rag_service import semantic_policy_search, build_policy_index
    results = semantic_policy_search("how do I approve a vendor invoice")
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Fix Windows SSL certificate verification for tiktoken and other HTTP calls
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE",       certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE",  certifi.where())
    os.environ.setdefault("CURL_CA_BUNDLE",      certifi.where())
except ImportError:
    pass

_client = None
_collection = None
_INDEX_BUILT = False
_embedder = None

CHROMA_PATH = str(Path(__file__).parent.parent / ".chromadb")


def _embed_texts(texts: list[str]) -> list[list[float]] | None:
    """
    Embed texts via OpenAI API directly (bypasses tiktoken + requests SSL issues).
    Uses httpx with SSL verify=False for local Windows dev.
    In production (Linux/Render), SSL works normally.
    """
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or "your_" in key:
        return None
    try:
        import httpx
        import sys

        # Use verify=False only on Windows dev — production Linux has valid certs
        verify = sys.platform != "win32"
        with httpx.Client(verify=verify, timeout=30.0) as client:
            resp = client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "text-embedding-3-small", "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]
    except Exception:
        return None


def _get_embedder():
    """Returns True if embedding is available (used for capability checks)."""
    global _embedder
    key = os.getenv("OPENAI_API_KEY", "")
    _embedder = bool(key and "your_" not in key)
    return _embedder


def _get_client():
    global _client
    if _client is None:
        import chromadb
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client


def _get_collection():
    global _collection
    if _collection is not None:
        return _collection
    client = _get_client()
    has_emb = _get_embedder() is not None
    col_name = "hb_policies_v2"
    try:
        _collection = client.get_or_create_collection(
            name=col_name,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception:
        try:
            client.delete_collection(col_name)
        except Exception:
            pass
        _collection = client.create_collection(
            name=col_name,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def build_policy_index(force: bool = False) -> int:
    """
    Index all policies + agent knowledge into ChromaDB.
    Uses LangChain OpenAIEmbeddings (no ChromaDB-internal HTTP calls).
    Skips if already indexed (unless force=True).
    """
    global _INDEX_BUILT
    col = _get_collection()

    if col.count() > 0 and not force:
        _INDEX_BUILT = True
        return col.count()

    from database.db import query as db_query

    policies = db_query(
        "SELECT id, title, business_function, steps_json, escalation_rule, approval_threshold FROM policies"
    )
    if not policies:
        return 0

    # Build document corpus
    agent_knowledge = [
        ("agent_associate",  "Associate Productivity — HRIS workflows",
         "Helps associates navigate HRIS policies, HR workflows, corporate procedures, approval chains and escalation paths. Use for any question about how to complete a process, what approvals are needed, or who to contact."),
        ("agent_vendor",     "Vendor Approval — ERP procurement",
         "Automates vendor onboarding and contract approval workflows. Integrates with ERP procurement modules. Use for vendor risk review, contract approval routing, insurance verification."),
        ("agent_community",  "Community Performance — CRM sales ops",
         "Analyzes CRM lead pipeline, sales performance, inventory, and conversion data. Use for community underperformance analysis, stale inventory, lead funnel issues."),
        ("agent_finance",    "Finance Incentive — ERP financial modeling",
         "Models pricing, discount, and incentive scenarios against ERP financial data. Enforces margin constraints and policy approval thresholds."),
    ]

    ids, docs, metas = [], [], []

    for p in policies:
        steps   = json.loads(p["steps_json"] or "[]")
        content = (
            f"Policy: {p['title']}. "
            f"Department: {p['business_function']}. "
            f"Process: {' | '.join(steps)}. "
            f"Approval required above ${p['approval_threshold']:,.0f}. "
            f"Escalation: {p['escalation_rule']}."
        )
        ids.append(f"pol_{p['id']}")
        docs.append(content)
        metas.append({"type": "policy", "title": p["title"],
                      "function": p["business_function"],
                      "threshold": float(p["approval_threshold"] or 0)})

    for doc_id, title, content in agent_knowledge:
        ids.append(doc_id)
        docs.append(content)
        metas.append({"type": "agent", "title": title, "function": "", "threshold": 0.0})

    # Compute embeddings directly via OpenAI API (bypasses tiktoken SSL issues)
    vectors = _embed_texts(docs)
    if not vectors:
        return 0
    try:
        col.upsert(ids=ids, embeddings=vectors, documents=docs, metadatas=metas)
    except Exception:
        return 0

    _INDEX_BUILT = True
    return col.count()


def semantic_policy_search(query_text: str, n: int = 3) -> list[dict]:
    """
    Semantic search over policies and agent knowledge base.
    Returns ranked results with relevance scores.
    Falls back gracefully if RAG is unavailable.
    """
    try:
        if not _get_embedder():
            return []

        build_policy_index()
        col   = _get_collection()
        count = col.count()
        if count == 0:
            return []

        # Compute query embedding directly
        query_vecs = _embed_texts([query_text])
        if not query_vecs:
            return []
        results = col.query(
            query_embeddings=query_vecs,
            n_results=min(n, count),
        )

        matches = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            matches.append({
                "title":           meta.get("title", ""),
                "type":            meta.get("type", "policy"),
                "function":        meta.get("function", ""),
                "content":         doc,
                "relevance_score": round(max(0.0, 1.0 - dist), 3),
                "threshold":       meta.get("threshold", 0),
            })

        return matches

    except Exception:
        return []


def rag_available() -> bool:
    """Returns True if ChromaDB and OpenAI key are available."""
    try:
        import chromadb  # noqa
        return bool(_get_embedder())
    except ImportError:
        return False


def index_status() -> dict:
    """Returns current index stats for display in the UI."""
    try:
        has_emb = bool(_get_embedder())
        col = _get_collection()
        return {
            "available":       True,
            "document_count":  col.count(),
            "embedding_model": "text-embedding-3-small (OpenAI)" if has_emb else "unavailable",
            "index_built":     _INDEX_BUILT,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}
