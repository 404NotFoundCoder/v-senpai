import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from api.embed_utils import cohere_embed_with_fallback

# 載入 .env
load_dotenv()

# title = question+(interviewee) 文章標題
# content = 根據interviewee的經驗，answer 內文


def upload_to_pinecone(id, title, content, comment=None):
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    if not pinecone_api_key:
        print("❌ 請確認 .env 中是否正確設定 PINECONE_API_KEY")
        return

    # 初始化 Pinecone
    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "vec-test-1"

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

    print(
        f"🔍 正在處理 ID: {id}，文本內容: {content}"
        + (f"，留言: {comment}" if comment else "")
    )

    embedding = cohere_embed_with_fallback(content, input_type="search_document")

    vectors.append(
        {
            "id": id,
            "values": embedding,
            "metadata": {
                "source": title,
                "content": content,
                **({"comment": comment} if comment else {}),
            },
        }
    )

    try:
        index.upsert(vectors=vectors)
        print(f"✅ 成功上傳 {len(vectors)} 筆向量到 Pinecone index `{index_name}`！")
    except Exception as e:
        print(f"❌ 上傳失敗：{e}")
