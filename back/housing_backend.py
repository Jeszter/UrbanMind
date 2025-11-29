import os
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from openai import OpenAI

load_dotenv()

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

housing_system_prompt = """
You are an AI assistant for migrants focused on housing and daily life.
Always respond in the same language as the user's last message.
Explain how people typically search for housing, what costs to expect and how everyday services work.
Do not promise specific prices or legal conditions; give only general guidance.
"""

@router.post("/chat")
async def housing_chat(request: Request):
    data = await request.json()
    message = (data.get("message") or "").strip()
    if not message:
        return JSONResponse({"status": "error", "message": "Message is empty."}, status_code=400)
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": housing_system_prompt},
                {"role": "user", "content": message},
            ],
        )
        reply = response.choices[0].message.content
        return JSONResponse({"status": "success", "reply": reply})
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Housing chat error: {str(e)}"}, status_code=500)
