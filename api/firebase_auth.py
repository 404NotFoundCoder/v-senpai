import json
import os
from pathlib import Path
from typing import Tuple

import firebase_admin
from firebase_admin import auth, credentials, get_app


def _load_service_account_cred():
    """
    憑證來源（優先順序）：
    1. 環境變數 FIREBASE_SERVICE_ACCOUNT_JSON（整份 Service Account JSON 字串）— 適用 Vercel / 生產
    2. 專案根目錄 key.json — 僅本機開發
    """
    raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    if raw:
        return credentials.Certificate(json.loads(raw))

    project_root = Path(__file__).resolve().parent.parent
    service_account_path = project_root / "key.json"
    if not service_account_path.is_file():
        raise FileNotFoundError(
            "找不到 Firebase 憑證：請設定環境變數 FIREBASE_SERVICE_ACCOUNT_JSON，"
            "或在專案根目錄放置 key.json（僅本機）。"
        )
    return credentials.Certificate(str(service_account_path))


def init_firebase_admin() -> None:
    """初始化 Firebase Admin（僅初始化一次）。"""
    try:
        get_app()
        return
    except ValueError:
        pass

    cred = _load_service_account_cred()
    firebase_admin.initialize_app(cred)


def verify_id_token_and_create_custom_token(id_token: str) -> Tuple[str, str]:
    """
    驗證 ID Token 並建立 Custom Token。

    Returns:
        (custom_token, uid)
    """
    init_firebase_admin()

    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token.get("uid")
    if not uid:
        raise ValueError("ID Token 驗證失敗，無法取得 UID")

    custom_token_bytes = auth.create_custom_token(uid)
    custom_token = custom_token_bytes.decode("utf-8")
    return custom_token, uid
