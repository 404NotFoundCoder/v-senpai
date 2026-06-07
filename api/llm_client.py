import json
from typing import Dict, List

from openai import OpenAI

# deploy開
from api.vector_search import vector_search_by_source_type_decision, vector_search_light

# local開
# from vector_search import (
#     vector_search_light,
# )


# token = os.environ["GITHUB_TOKEN"]
ENDPOINT = "https://models.inference.ai.azure.com"
MODEL_NAME = "gpt-4o-mini"

SOURCE_TYPE_CLASSIFIER_PROMPT = """
你是輔仁大學資管系「系統分析與設計」課程的檢索來源分類器。

請判斷使用者這次問題應該優先使用哪一類資料進行檢索。

只能使用以下其中一個標籤：

- peer_sharing：
  使用者需要學長姐經驗、同儕討論、實際修課經驗、過去學生案例、論壇式建議、主觀意見、修課心得或實際經驗分享。

- teaching_material：
  使用者需要課程內容說明、概念解釋、定義、結構化知識、課程教材、作業規定要求、評分標準、文件撰寫規範、課程進度或教學資料。

- mixed：
  使用者的問題同時可能需要學長姐經驗(peer_sharing)與課程教材(teaching_material)，或兩者都可能有幫助，或問題意圖不夠明確。

請只回傳合法 JSON，不要加入任何解釋文字。
"""

# LLM 分類只代表「這次問題應該怎麼查資料」；
# references 裡的 sourceType 則是文件 metadata，代表該文件本身的來源種類。
SOURCE_TYPE_CLASSIFIER_SCHEMA = {
    "name": "source_type_classification",
    "schema": {
        "type": "object",
        "properties": {
            "sourceType": {
                "type": "string",
                "enum": ["peer_sharing", "teaching_material", "mixed"],
            }
        },
        "required": ["sourceType"],
        "additionalProperties": False,
    },
}


V_SENPAI_SYSTEM_PROMPT = """
你是「V-Senpai」，一位具備豐富經驗的學長姊模擬機器人。你的任務是協助學生了解輔仁大學資管系「系統分析與設計」課程（又稱 SA、小專題）與「專題實作」之間的差異與歷屆經驗。
你會根據歷屆學生的訪談紀錄與課程背景知識，扮演一位中文課堂助教，幫助學生釐清困惑、提供建議與經驗分享。
請嚴格遵守以下規則：
1. **只回答 Final Question。**
   - 只針對 Final Question 進行回答，非必要不要回答過往聊天紀錄中的舊問題。
2. **資料為本，禁止猜測或捏造資訊。**  
   - 回答只能根據資料中出現的內容（例如：訪談、課程規劃等）但必須符合使用者Final Question問題。  
   - 若找不到答案，請說：「我找不到相關資料」，並鼓勵學生改問其他角度。但若屬通用知識則可補充，但必須先聲明「資料中未提及，以下為一般知識補充」。
3. **問題模糊時，協助釐清再回答。**  
   - 若學生問題不清楚，請主動列出選項或追問，協助對方聚焦。  
4. **回答方式要具體、真誠、有條理。**  
   - 舉例時請指出是來自「某位同學的經驗」。  
   - 可引用「某位同學的經驗」或「訪談內容」，避免空泛建議如「多努力」，這類無實質幫助的回答。  
5. **以自然口語中文作答**，簡潔清晰，不過於冗長，讓使用者能夠清晰理解內容。
6. **重要連結需特別列出。**
   - 若參考資料中出現重要連結，尤其是**教材來源**、課程網站、學習資源、範例文件、表單或系統連結，回答時需在文末另列「參考連結」區塊。
   - 禁止列出資料沒有提供之連結，也禁止自行編造。
   - 連結說明需簡短清楚
   - 若沒有特別重要的連結或沒有出現連結，則不需要列出「參考連結」區塊。
"""

AI_DRAFT_SYSTEM_PROMPT = """
You are an assistant that helps users write a forum help post when the chatbot fails to solve their problem.

The user provides:
1. Their final unsatisfied question (the real problem they still want help with)
2. The conversation history with the chatbot (background context)

Your task is:
- Focus primarily on the final question to understand the core issue.
- Use the conversation history only as supporting context.
- Ignore unrelated or outdated messages.
- Infer missing details if necessary.

Write a natural, human-like forum help post as if the user is directly asking for help.

Important rules:
- Do NOT mention the chatbot, AI, or conversation history.
- Keep the post concise but clear.

Output strictly in valid JSON with the following structure:

{
  "title": "string",
  "post": "string",
  "key_points": [
    "string",
    "string",
    "string"
  ]
}

Do not include any explanation.
Only output valid JSON.
"""
ARTICLE_REVIEW_SYSTEM_PROMPT = """
你是一個輔仁大學資管系「系統分析與設計 SA 課程論壇」的文章審核助手。

你的任務是根據學生投稿的論壇文章 title 和 content，判斷該文章是否適合公開給其他學生觀看。

論壇用途：
- 分享 SA 課程、小專題、系統開發、文件撰寫、團隊合作與課程經驗等內容。
- 學生可以提出問題、抱怨、分享困難或表達負面感受。
- 但文章仍須維持基本尊重，不應包含人身攻擊、惡意造謠、隱私外洩、威脅、歧視、色情、灌水或明顯無關內容。

請根據文章標題和內容回傳以下其中一種 status：

1. approved
文章可以公開。
適用情況：
- 正常提問。
- 分享 SA 課程或小專題經驗。
- 抱怨課程困難、文件很多、組員不配合、壓力大，但沒有攻擊特定個人。
- 批評課程安排、系統開發流程或團隊合作問題，但語氣仍可接受。
- 內容雖有負面情緒，但主要是在描述學習困難或尋求協助。
- 沒有明顯人身攻擊、隱私外洩、威脅、歧視、色情、灌水或嚴重誤導資訊。

2. rejected
文章明顯不適合公開。
適用情況：
- 亂碼、灌水、廣告、惡作劇，或完全與 SA 課程論壇無關。
- 惡意辱罵、霸凌、羞辱或攻擊特定老師、助教、同學、組員。
- 攻擊他人的人格、外貌、能力、背景，而不是批評具體事件。
- 鼓吹集體攻擊、騷擾、報復或其他惡意行為。
- 公開他人隱私資訊，例如學號、電話、Email、住址、私人對話內容等。
- 包含威脅、暴力、仇恨、歧視、色情或明顯不適合學生論壇公開的內容。
- 散布嚴重錯誤資訊，且可能明顯誤導其他學生。
- 內容明顯是來亂、無意義或惡意破壞論壇品質。

3. review_manually
AI 無法可靠判斷，或文章需要管理員根據課程實際情況確認。
適用情況：
- 文章可能需要修改，但不確定是否應拒絕。
- 語氣偏激、情緒強烈，但是否構成人身攻擊需要人工判斷。
- 有影射特定對象，但沒有明確姓名或上下文不足。
- 文章提到具體課程規定、評分方式、作業要求、繳交期限，但無法確認是否正確。
- 文章內容模糊，無法判斷是否為惡意、造謠或正常抱怨。
- 文章可能涉及真實糾紛，需要人工判斷。
- 文章看似有問題，但缺乏足夠上下文。
- 文章沒有嚴重到 rejected，但也不適合讓 AI 直接 approved。
- AI 無法明確判斷應該通過或拒絕時。

issues 欄位請根據文章問題選擇，可使用：
- spam_or_irrelevant：灌水、廣告、亂碼、明顯無關內容
- misleading_information：可能誤導學生的課程資訊、規定、評分或期限
- personal_attack：人身攻擊、羞辱、霸凌、針對特定個人
- privacy_issue：公開不適合公開的個人資訊
- extreme_or_inflammatory：過激、煽動、鼓吹惡意行為
- hate_or_discrimination：仇恨或歧視內容
- threat_or_violence：威脅或暴力內容
- sexual_content：色情或不適合學生論壇的性內容
- unclear：內容模糊、上下文不足，無法可靠判斷
- none：沒有明顯問題

審核原則：
- 不要因為文章有負面情緒就拒絕。
- 學生可以抱怨課程很難、組員不配合、文件很多、壓力大。
- 批評事情可以接受，但攻擊人不可接受。
- 只有在文章明顯安全且適合公開時，才使用 approved。
- 只有在文章明顯不適合公開時，才使用 rejected。
- 只要文章可能需要修改、語氣需要人工判斷、資訊真假無法確認、或上下文不足，請使用 review_manually。
- 若無法判斷真假、嚴重程度或是否適合公開，請使用 review_manually。
- 若文章沒有明顯問題，請使用 approved，issues 填入 ["none"]。
- 若 status 是 approved，problematic_quote 請回傳空字串。
- 若 status 是 rejected 或 review_manually，problematic_quote 請填入最主要有疑慮的片段；若無明確片段，請回傳空字串。
- reason 請簡短說明判斷原因，不要太長。

user_message 欄位規則：
- 只有當 status 是 rejected 時，user_message 才需要填寫。
- rejected 的 user_message 請用溫和、清楚、不羞辱使用者的語氣，說明文章未通過的原因。
- 不要只寫「文章不符合規範」。
- 要簡短指出主要問題，例如：文章包含人身攻擊、隱私資訊、威脅、廣告或與論壇無關內容。
- 可以提醒使用者修改後再重新投稿。
- 若 status 是 approved 或 review_manually，user_message 請回傳空字串 ""。

請只回傳符合 schema 的 JSON，不要輸出任何多餘說明。
"""

ARTICLE_REVIEW_SCHEMA = {
    "name": "article_review_result",
    "schema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["approved", "rejected", "review_manually"],
                "description": "文章審核結果",
            },
            "reason": {
                "type": "string",
                "description": "給管理員看的簡短審核原因",
            },
            "user_message": {
                "type": "string",
                "description": "只有 status 為 rejected 時才填寫給發文者看的拒絕原因；其他狀態請回傳空字串",
            },
            "issues": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "spam_or_irrelevant",
                        "misleading_information",
                        "personal_attack",
                        "privacy_issue",
                        "extreme_or_inflammatory",
                        "hate_or_discrimination",
                        "threat_or_violence",
                        "sexual_content",
                        "unclear",
                        "none",
                    ],
                },
                "description": "文章可能存在的問題；若沒有問題則填 none",
            },
            "problematic_quote": {
                "type": "string",
                "description": "最主要有問題的片段；若沒有則回傳空字串",
            },
        },
        "required": [
            "status",
            "reason",
            "user_message",
            "issues",
            "problematic_quote",
        ],
        "additionalProperties": False,
    },
}


def format_history_for_chat(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    messages = []
    for pair in history:
        user_msg = pair.get("user")
        ai_msg = pair.get("ai")

        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if ai_msg:
            messages.append({"role": "assistant", "content": ai_msg})
    messages.append(
        {
            "role": "user",
            "content": "---------------------\n以上是過往的聊天紀錄，請參考。\n--------------------",
        }
    )
    return messages


def classify_question_source_type(client: OpenAI, user_input: str) -> str:
    """用 LLM 判斷本次問題要優先查哪種來源；失敗時保守視為 mixed。"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SOURCE_TYPE_CLASSIFIER_PROMPT},
                {"role": "user", "content": user_input},
            ],
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": SOURCE_TYPE_CLASSIFIER_SCHEMA,
            },
        )
        result = json.loads(response.choices[0].message.content)
        source_type = result.get("sourceType", "mixed")
        if source_type in {"peer_sharing", "teaching_material", "mixed"}:
            return source_type
    except Exception as e:
        print("sourceType classification failed:", str(e))

    return "mixed"


def get_vector_search_result(user_input: str, token: str = None) -> dict:
    """只進行向量搜尋，不回傳 LLM 回應"""
    if token:
        client = OpenAI(base_url=ENDPOINT, api_key=token)
        # /api/search 有 accessToken 時會先分類，再依分類結果搜尋。
        source_type_decision = classify_question_source_type(client, user_input)
        search_result = vector_search_by_source_type_decision(
            user_input, source_type_decision, 3
        )
    else:
        search_result = vector_search_light(user_input)
    print("🔍 向量搜尋結果:", search_result)

    return {
        "sources": search_result.get("sources", []),
        "ids": search_result.get("ids", []),
        "sourceTypes": search_result.get("sourceTypes", []),
        "sourceTypeDecision": search_result.get("sourceTypeDecision"),
        "references": search_result.get("references", []),
        "matches": search_result.get("matches", []),
        "context_text": search_result.get("context_text", "查無資料。"),
    }


def get_openai_response(
    token: str,
    user_input: str,
    context_text: str = None,
    history=None,
    references=None,
    source_types=None,
    source_type_decision=None,
) -> str:
    client = OpenAI(
        base_url=ENDPOINT,
        api_key=token,
    )
    references = references or []
    source_types = source_types or []
    # 已有 context_text 時沿用前一步搜尋結果；沒有 context_text 時才分類並搜尋。
    if context_text is None:
        source_type_decision = classify_question_source_type(client, user_input)
        search_result = vector_search_by_source_type_decision(
            user_input, source_type_decision, 3
        )
        context_text = search_result.get("context_text", "查無資料。")

        references = search_result.get("references", [])
        source_types = search_result.get("sourceTypes", [])
    elif not source_types and references:
        source_types = [ref.get("sourceType", "unknown") for ref in references]

    messages = [
        {
            "role": "system",
            "content": V_SENPAI_SYSTEM_PROMPT
            + f"\n\n以下是你可以參考的資料（RAG Context）：\n{context_text}---"
            + ("\n以下是過往的聊天紀錄：" if history else ""),
        },
        *(format_history_for_chat(history) if history else []),
        {
            "role": "user",
            "content": f"Final Question (請只回答這一問題): {user_input}",
        },
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME, messages=messages, temperature=1.0, top_p=1.0
    )

    print("AI回覆", response.choices[0].message.content)
    print("AI回覆使用的上下文資料:", context_text)

    return {
        "answer": response.choices[0].message.content,
        "context": context_text,
        "references": references,
        "sourceTypes": source_types,
        "sourceTypeDecision": source_type_decision,
    }


def get_openai_draft_article(token: str, history: object, final_question: str) -> str:
    client = OpenAI(
        base_url=ENDPOINT,
        api_key=token,
    )

    messages = [
        {
            "role": "system",
            "content": AI_DRAFT_SYSTEM_PROMPT + "\n以下是conversation history：",
        },
        *format_history_for_chat(history),
        {
            "role": "user",
            "content": f"Final Question (the user still wants help with): {final_question}",
        },
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME, messages=messages, temperature=1.0, top_p=1.0
    )

    print("AI草稿文章", response.choices[0].message.content)
    return {
        "draft": response.choices[0].message.content,
    }


def review_forum_article(token: str, title: str, content: str) -> dict:
    client = OpenAI(
        base_url=ENDPOINT,
        api_key=token,
    )

    messages = [
        {
            "role": "system",
            "content": ARTICLE_REVIEW_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
請審核以下 SA 課程論壇文章。

【標題】
{title}

【內容】
{content}
""",
        },
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": ARTICLE_REVIEW_SCHEMA,
        },
    )

    result_text = response.choices[0].message.content

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {
            "status": "review_manually",
            "reason": "AI 回傳格式無法解析，建議交由管理員人工審核。",
            "issues": ["unclear"],
            "problematic_quote": "",
        }
