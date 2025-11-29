import os
import json
from typing import List, Literal, Optional, Dict, Any

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

COOKIE_NAME = "language_tutor_state"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class LanguageChatRequest(BaseModel):
    messages: List[ChatMessage]
    ui_language: Optional[str] = "ru"


class CheckItem(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_option_index: int


class CheckRequest(BaseModel):
    answers: Dict[str, Optional[int]]
    exercises: List[CheckItem]
    target_language: Optional[str]
    estimated_level: Optional[str]


language_tutor_system_prompt = """
You are an AI language tutor.

Administrative and meta rules:
- All administrative text, instructions, task descriptions, and service phrases must always be in English, regardless of the target language or UI language.
- The target language should appear mainly in the content of the exercises and example sentences, not in the meta instructions.

Interaction rules:
- Whenever the learner answers any question or exercise, you must immediately:
  1) Say clearly whether the answer is correct or incorrect.
  2) Show the correct answer.
  3) Give a short, simple explanation of the rule.
  4) Give 1–2 short example sentences in the target language.
- Do not postpone the review. Never say only "Let's review your answer" without the actual review. The full review must be included in the same assistant_message.
- Keep explanations short and easy to understand.
- Do not repeat the same type of practice indefinitely. After each set of exercises you must clearly ask the learner what they want to do next.

Goals:
1) For a completely new learner with no profile: greet them in English and ask which language they want to learn.
2) After the target language is chosen for a new learner, ask 3–5 short questions or mini tasks in that target language to estimate their CEFR level (A1, A2, B1, B2, C1). Ask them not to use any translators or help. The instructions for these tasks must still be in English.
3) When you have enough information for a new learner, clearly state the estimated CEFR level in English.
4) For a returning learner with an existing profile: do not repeat the level test. Greet them briefly, remind them of their level and target language, and continue with practice.
5) When the learner chooses the focus, generate 3–4 short exercises of that type, adapted to their level. Instructions for each exercise are in English; example sentences and words are mostly in the target language.
6) After each set of exercises or after reviewing test answers, always ask in English what the learner wants to practice next (for example: grammar, vocabulary, listening, review of mistakes, or something else) and wait for their choice in the next message.

Exercises:
- Grammar: gap-filling, choose the correct form, simple sentence transformation.
- Vocabulary: choose correct translation, match word with definition, choose the best word to complete a sentence.
- Listening: provide a short transcript (1–3 sentences) and questions about it. The transcript should be mostly in the target language, but all questions and instructions remain in English.

Response format for /chat:
You must always respond with a single valid JSON object, no extra text, no markdown.

Schema:

{
  "assistant_message": "string, main reply to show in chat",
  "phase": "language_choice" | "level_test" | "focus_choice" | "practice",
  "target_language": "string or null, ISO code or name",
  "estimated_level": "A1" | "A2" | "B1" | "B2" | "C1" | null,
  "practice_type": "grammar" | "vocabulary" | "listening" | null,
  "exercises": {
    "type": "grammar" | "vocabulary" | "listening",
    "items": [
      {
        "id": "string",
        "question": "string",
        "options": ["string", "string", ...],
        "correct_option_index": 0
      }
    ]
  }
}

Rules:
- If you are still choosing language or checking level, you may set exercises to null.
- When practice_type is not null, you must provide 3–4 exercise items.
- assistant_message should be friendly and short, but must contain the review of the learner's latest answers when they have just answered a question.
- At the end of assistant_message you must include a clear question in English asking what the learner wants to practice next.

For /check:
You receive a JSON object with learner answers and the correct options. You must return JSON in this format:

{
  "assistant_message": "string",
  "feedback": [
    {
      "id": "string",
      "correct": true or false,
      "user_answer": "string",
      "correct_answer": "string",
      "explanation": "string"
    }
  ]
}

Each explanation should be short, in English, and may include 1–2 example sentences in the target language.
The assistant_message for /check must always end with a clear question in English asking what the learner wants to do next (for example: "What would you like to practice next: grammar, vocabulary, listening, or review more of these mistakes?").
"""



def load_state_from_cookie(request: Request) -> Dict[str, Any]:
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def save_state_to_cookie(response: Response, state: Dict[str, Any]) -> None:
    try:
        value = json.dumps(state)
    except Exception:
        return
    response.set_cookie(
        key=COOKIE_NAME,
        value=value,
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite="lax",
    )


def merge_state(prev: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(prev)
    for key in ["target_language", "estimated_level", "practice_type", "phase"]:
        if key in new and new[key] is not None:
            merged[key] = new[key]
    return merged


@router.post("/chat")
async def language_chat(payload: LanguageChatRequest, request: Request, response: Response):
    ui_lang = payload.ui_language or "ru"
    learner_state = load_state_from_cookie(request)

    messages_for_model: List[Dict[str, str]] = [
        {"role": "system", "content": language_tutor_system_prompt.strip()}
    ]

    if learner_state:
        profile_text = json.dumps(learner_state, ensure_ascii=False)
        messages_for_model.append(
            {
                "role": "system",
                "content": (
                    "Saved learner profile. The learner is returning. "
                    "Use this profile to continue from their current target language and level. "
                    "Do not repeat the level test unless the learner explicitly asks to restart.\n"
                    f"Learner profile JSON: {profile_text}"
                ),
            }
        )

    if not payload.messages:
        if learner_state:
            start_text = (
                f"UI language for the web interface is: {ui_lang}. "
                f"The learner is returning. Continue the tutoring session using the saved profile. "
                f"Do not restart the level test. Start with a short greeting and then continue practice."
            )
        else:
            start_text = (
                f"UI language for the web interface is: {ui_lang}. "
                f"The learner is new. Greet them in English and ask which language they want to learn."
            )
        messages_for_model.append({"role": "user", "content": start_text})
    else:
        for m in payload.messages:
            messages_for_model.append({"role": m.role, "content": m.content})

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages_for_model,
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        data: Dict[str, Any] = json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language tutor error: {str(e)}")

    if not isinstance(data, dict) or "assistant_message" not in data:
        raise HTTPException(status_code=500, detail="Invalid model response.")

    new_state_part = {
        "target_language": data.get("target_language"),
        "estimated_level": data.get("estimated_level"),
        "practice_type": data.get("practice_type"),
        "phase": data.get("phase"),
    }
    learner_state = merge_state(learner_state, new_state_part)
    save_state_to_cookie(response, learner_state)

    return {"status": "success", "data": data}


@router.post("/check")
async def check_answers(payload: CheckRequest):
    try:
        items = []
        for ex in payload.exercises:
            user_index = payload.answers.get(ex.id, None)
            user_answer = ex.options[user_index] if user_index is not None and 0 <= user_index < len(ex.options) else ""
            correct_answer = ex.options[ex.correct_option_index]
            correct_flag = user_index == ex.correct_option_index
            items.append(
                {
                    "id": ex.id,
                    "question": ex.question,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "correct": correct_flag,
                }
            )

        messages = [
            {
                "role": "system",
                "content": language_tutor_system_prompt.strip()
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "target_language": payload.target_language,
                        "estimated_level": payload.estimated_level,
                        "answers": items
                    },
                    ensure_ascii=False
                )
            }
        ]

        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        data = json.loads(resp.choices[0].message.content)
        return {"status": "success", "data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
