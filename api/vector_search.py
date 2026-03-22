import os
import sys

from dotenv import load_dotenv
from pinecone import Pinecone

from api.embed_utils import cohere_embed_with_fallback

# 設定標準輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()


def vector_search_light(user_input: str, top_k: int = 50) -> dict:
    try:
        # 初始化 Pinecone
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        index_name = "vec-test-1"
        index = pc.Index(index_name)

        # 取得向量
        vector = cohere_embed_with_fallback(user_input)

        # 查詢 Pinecone
        results = index.query(
            # namespace="interview-rag",
            vector=vector,
            top_k=top_k,
            include_values=False,
            include_metadata=True,
        )

        # 篩選 score > 0.5 的結果
        all_matches = results.get("matches", [])
        filtered_matches = [
            match for match in all_matches if match.get("score", 0) > 0.5
        ]

        # 取篩選後最高的三筆（可能少於三筆）
        top_three_matches = filtered_matches[:3]

        def _format_match(match: dict) -> str:
            metadata = match.get("metadata", {}) or {}
            source = metadata.get("source", "")
            content = metadata.get("content", "")
            comment = metadata.get("comment")

            base = f"標題：{source}\n內文：{content}"
            if comment:
                base += f"\n留言：{comment}"
            return base

        # 補一個合併所有文字的欄位（給 Prompt 用）- 使用篩選後最高的三筆
        formatted = "\n\n---\n\n".join(
            _format_match(match) for match in top_three_matches
        )
        # 來源文章標題
        sources = [match["metadata"]["source"] for match in top_three_matches]
        ids = [m["id"] for m in top_three_matches]

        references = []
        for match in top_three_matches:
            metadata = match.get("metadata", {}) or {}
            reference = {
                "id": match.get("id"),
                "source": metadata.get("source"),
                "content": metadata.get("content"),
            }
            if metadata.get("comment"):
                reference["comment"] = metadata.get("comment")
            references.append(reference)
        print("refrence", references)
        print(f"🔍 向量查詢結果數量: {len(filtered_matches)}")
        print(f"🔍 篩選後最高三筆數量: {len(top_three_matches)}")
        print("📊 向量查詢使用用量:", results.get("usage", {}))
        # print(f"🔍 向量查詢結果內容: {formatted[:200]}...")  # 只顯示前200個字
        print("------------------------------------")

        # 將 matches 轉換為可序列化的格式
        serializable_matches = []
        for match in filtered_matches:
            serializable_match = {
                "id": match.get("id"),
                "score": match.get("score"),
                "metadata": match.get("metadata", {}),
            }
            serializable_matches.append(serializable_match)
        print("🔍--------------------------------")
        print(
            {
                "matches": serializable_matches,
                "sources": sources,
                "ids": ids,
                "context_text": formatted,
                "references": references,
                "usage": results.get("usage", {}),
            }
        )

        return {
            "matches": serializable_matches,
            "sources": sources,
            "ids": ids,
            "context_text": formatted,  # ✅ 給 prompt 直接使用
            "references": references,
            "usage": results.get("usage", {}),
        }
    except Exception as e:
        print(f"❌ 向量查詢錯誤: {str(e)}")
        return {"matches": [], "text": "查無資料。", "usage": {}, "error": str(e)}
