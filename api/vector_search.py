import os
import sys

import cohere
from dotenv import load_dotenv
from pinecone import Pinecone

from api.embed_utils import cohere_embed_with_fallback

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

INDEX_NAME = "vec-0601"
VALID_SOURCE_TYPES = {"peer_sharing", "teaching_material"}


def _get_index():
    print(
        "🔑 正在使用的 Pinecone API Key:", os.environ.get("PINECONE_API_KEY", "未設定")
    )
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    return pc.Index(INDEX_NAME)


def _source_type_filter(source_type: str | None) -> dict | None:
    # sourceType 是文件本身的 metadata；Pinecone filter 只拿它來篩文件。
    if source_type not in VALID_SOURCE_TYPES:
        return None
    return {"sourceType": {"$eq": source_type}}


def _match_to_reference(match: dict) -> dict:
    metadata = match.get("metadata", {}) or {}
    # 回傳給前端的 sourceType 來自文件 metadata，不是 LLM 對問題的分類。
    reference = {
        "id": match.get("id"),
        "source": metadata.get("source"),
        "content": metadata.get("content"),
        "sourceType": metadata.get("sourceType", "unknown"),
    }
    if metadata.get("comment"):
        reference["comment"] = metadata.get("comment")
    if match.get("score") is not None:
        reference["score"] = match.get("score")
    if match.get("rerank_score") is not None:
        reference["rerank_score"] = match.get("rerank_score")
    return reference


def _reference_to_match(reference: dict) -> dict:
    metadata = {
        "source": reference.get("source"),
        "content": reference.get("content"),
        "sourceType": reference.get("sourceType", "unknown"),
    }
    if reference.get("comment"):
        metadata["comment"] = reference.get("comment")

    return {
        "id": reference.get("id"),
        "score": reference.get("score"),
        "rerank_score": reference.get("rerank_score"),
        "metadata": metadata,
    }


def _format_reference(reference: dict) -> str:
    # context_text 也保留 sourceType，讓回答模型知道每段資料的來源種類。
    text = (
        f"sourceType: {reference.get('sourceType', 'unknown')}\n"
        f"source: {reference.get('source', '')}\n"
        f"content: {reference.get('content', '')}"
    )
    if reference.get("comment"):
        text += f"\ncomment: {reference['comment']}"
    return text


def _build_result(matches: list[dict], source_type_decision: str | None = None) -> dict:
    references = [_match_to_reference(match) for match in matches]
    context_text = "\n\n---\n\n".join(_format_reference(ref) for ref in references)

    return {
        "matches": matches,
        "sources": [ref.get("source") for ref in references],
        "ids": [ref.get("id") for ref in references],
        "sourceTypes": [ref.get("sourceType", "unknown") for ref in references],
        "sourceTypeDecision": source_type_decision,
        "context_text": context_text,
        "references": references,
    }


def _rerank_text(candidate: dict) -> str:
    # rerank 只比較文件正文與留言；sourceType 保留在 metadata，不混入排序文字。
    text = candidate.get("content") or ""
    if candidate.get("comment"):
        text += f"\n{candidate['comment']}"
    return text


def rerank(query: str, candidates: list[dict], top_n: int = 3) -> list[dict]:
    """
    candidates format:
    [{"id": ..., "source": ..., "content": ..., "comment": ..., "sourceType": ...}, ...]
    """
    if not candidates:
        return []

    co = cohere.ClientV2(api_key=os.environ.get("CO_API_KEY_1"))
    documents = [_rerank_text(candidate) for candidate in candidates]
    result = co.rerank(
        model="rerank-multilingual-v3.0",
        query=query,
        documents=documents,
        top_n=min(top_n, len(documents)),
    )

    reranked = []
    for item in result.results:
        original = candidates[item.index]
        reranked.append({**original, "rerank_score": item.relevance_score})

    return reranked


def vector_search_light(
    user_input: str, top_k: int = 50, source_type: str | None = None
) -> dict:
    try:
        index = _get_index()
        vector = cohere_embed_with_fallback(user_input)

        query_kwargs = {
            "vector": vector,
            "top_k": top_k,
            "include_values": False,
            "include_metadata": True,
        }
        source_filter = _source_type_filter(source_type)
        if source_filter:
            # 單一類型問題：只查 LLM 判斷出的那一種文件。
            query_kwargs["filter"] = source_filter

        results = index.query(**query_kwargs)
        all_matches = results.get("matches", [])
        filtered_matches = [
            match for match in all_matches if match.get("score", 0) > 0.5
        ]
        top_matches = filtered_matches[:top_k]

        serializable_matches = []
        for match in top_matches:
            serializable_matches.append(
                {
                    "id": match.get("id"),
                    "score": match.get("score"),
                    "metadata": match.get("metadata", {}),
                }
            )

        result_payload = _build_result(serializable_matches, source_type)
        result_payload["usage"] = results.get("usage", {})

        print("references", result_payload["references"])
        print(f"vector search filtered count: {len(filtered_matches)}")
        print(f"vector search returned count: {len(top_matches)}")
        print("vector search usage:", results.get("usage", {}))

        return result_payload
    except Exception as e:
        print(f"vector search error: {str(e)}")
        return {
            "matches": [],
            "sources": [],
            "ids": [],
            "sourceTypes": [],
            "sourceTypeDecision": source_type,
            "context_text": "No relevant context found.",
            "references": [],
            "usage": {},
            "error": str(e),
        }


def vector_search_by_source_type_decision(
    user_input: str, source_type_decision: str, top_k: int = 3
) -> dict:
    # peer_sharing / teaching_material：直接用 metadata filter 查該類 top_k。
    if source_type_decision in VALID_SOURCE_TYPES:
        return vector_search_light(
            user_input, top_k=top_k, source_type=source_type_decision
        )

    if source_type_decision != "mixed":
        return vector_search_light(user_input, top_k=top_k)

    # mixed：兩種來源各查 top_k，再合併去重後交給 Cohere rerank，最後只取 top_k。
    candidates = []
    usages = []
    for source_type in sorted(VALID_SOURCE_TYPES):
        result = vector_search_light(user_input, top_k=top_k, source_type=source_type)
        print(f"正在進行 sourceType={source_type}")
        candidates.extend(result.get("references", []))
        usages.append({source_type: result.get("usage", {})})

    deduped_candidates = {}
    for candidate in candidates:
        candidate_id = candidate.get("id")
        if candidate_id and candidate_id not in deduped_candidates:
            deduped_candidates[candidate_id] = candidate

    reranked_references = rerank(
        user_input, list(deduped_candidates.values()), top_n=top_k
    )
    matches = [_reference_to_match(reference) for reference in reranked_references]
    result = _build_result(matches, "mixed")
    result["usage"] = usages
    return result
