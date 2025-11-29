import os
import json
from typing import List, Literal, Optional, Dict, Any

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class LanguageChatRequest(BaseModel):
    messages: List[ChatMessage]
    ui_language: Optional[str] = "ru"


language_tutor_system_prompt = """
You are an AI language tutor.

Goals:
1) Start by greeting the learner and asking which language they want to learn.
2) After the target language is chosen, ask 3–5 short questions or mini tasks in that language to estimate their CEFR level (A1, A2, B1, B2, C1). Ask them not to use any translators or help.
3) When you have enough information, clearly state the estimated CEFR level.
4) Then ask what they want to focus on now: grammar, vocabulary, or listening.
5) When the learner chooses focus, generate 3–4 short exercises of that type, adapted to their level.

Exercises:
- Grammar: gap-filling, choose the correct form, simple sentence transformation.
- Vocabulary: choose correct translation, match word with definition, choose the best word to complete a sentence.
- Listening: since you cannot play audio, provide a short transcript (1–3 sentences) and questions about it. Mention that the learner should imagine listening to it.

Response format:
You must always respond with a single valid JSON object, no extra text, no markdown.
Use this schema:

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
- assistant_message should be friendly and short.
- Use simple Russian for meta explanations when ui_language is Russian, but most of the exercise content should be in the target language.
"""


@router.post("/chat")
async def language_chat(payload: LanguageChatRequest):
    ui_lang = payload.ui_language or "ru"
    messages_for_model = [{"role": "system", "content": language_tutor_system_prompt.strip()}]

    if not payload.messages:
        start_text = (
            f"UI language for explanations: {ui_lang}. "
            f"Start a new tutoring session. Greet the learner and ask which language they want to learn."
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
        )
        content = resp.choices[0].message.content
        data: Dict[str, Any] = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model returned invalid JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language tutor error: {str(e)}")

    if not isinstance(data, dict) or "assistant_message" not in data:
        raise HTTPException(status_code=500, detail="Model response has wrong structure.")

    return {"status": "success", "data": data}
