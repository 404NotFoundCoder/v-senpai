import os
import sys

import cohere
from dotenv import load_dotenv

# 設定標準輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

COHERE_KEYS = [
    os.getenv("CO_API_KEY_1"),
    os.getenv("CO_API_KEY_2"),
    os.getenv("CO_API_KEY_3"),
    os.getenv("CO_API_KEY_4"),
]


def cohere_embed_with_fallback(text: str, input_type="search_query"):
    last_error = None

    for i, key in enumerate(COHERE_KEYS):
        try:
            co = cohere.ClientV2(api_key=key)

            response = co.embed(
                texts=[text],
                model="embed-multilingual-v3.0",
                input_type=input_type,
                embedding_types=["float"],
            )

            return response.embeddings.float_[0]

        except Exception as e:

            error_str = str(e)

            if "429" in error_str or "Trial key" in error_str or "limit" in error_str:
                print(
                    f"⚠️ Cohere quota reached ( key {i+1} 額度用完), switching key{i+2}..."
                )
                last_error = e
                continue

            raise e

    raise Exception(f"All Cohere keys exhausted: {last_error}")
