import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from api.embed_utils import cohere_embed_with_fallback

# 載入 .env
load_dotenv()

# title = question+(interviewee) 文章標題
# content = 根據interviewee的經驗，answer 內文


def upload_to_pinecone(id, title, content, comment=None, source_type=None):
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    if not pinecone_api_key:
        print("❌ 請確認 .env 中是否正確設定 PINECONE_API_KEY")
        return

    # 初始化 Pinecone
    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "vec-0601"

    if index_name not in pc.list_indexes().names():
        print(f"⚙️ 建立新的 Pinecone index: {index_name} (serverless)...")
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)

    vectors = []

    if comment is not None and str(comment).strip() == "":
        comment = None

    # sourceType 會寫進 Pinecone metadata，後續搜尋會用它篩選文件種類。
    # 舊呼叫端若尚未傳 sourceType，先用 peer_sharing 維持既有上傳流程可用。
    if source_type not in {"peer_sharing", "teaching_material"}:
        source_type = "peer_sharing"

    embed_text = (
        f"標題:{title}\n內文:{content}\n{comment}"
        if comment
        else f"標題:{title}\n內文:{content}"
    )
    print(f"🔍 處理 ID: {id}，標題: {title}" + ("（含留言）" if comment else ""))

    embedding = cohere_embed_with_fallback(embed_text, input_type="search_document")

    vectors.append(
        {
            "id": id,
            "values": embedding,
            "metadata": {
                "source": title,
                "content": content,
                # 這是文件自己的類型，不是使用者問題的 LLM 分類結果。
                "sourceType": source_type,
                **({"comment": comment} if comment else {}),
            },
        }
    )

    try:
        index.upsert(vectors=vectors)
        print(f"✅ 成功上傳 {len(vectors)} 筆向量到 Pinecone index `{index_name}`！")
    except Exception as e:
        print(f"❌ 上傳失敗：{e}")
