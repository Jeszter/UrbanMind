import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    chat_history: list = []
    ui_language: str = "en"

urbanmind_system_prompt = """
You are an AI assistant for UrbanMind platform that helps migrants adapt to a new country.

Your main functions:
1. Help with navigation through UrbanMind website
2. Direct users to relevant sections
3. Answer questions about platform capabilities

Main website sections and their paths:
- Improve or check CV: /neurohr
- Find jobs: /jobs  
- Language learning: /language
- Official forms and office search: /official
- Translation services: /translation
- Cultural attractions: /cultural

Interaction rules:
- Respond in a friendly and helpful manner
- If user asks for help with specific task, suggest relevant section
- Provide brief section description before directing there
- If unsure about answer, suggest contacting support
- Respond in user's language (mainly English)
- Use quick actions for easy navigation

Always end your response by offering help with something else.
"""

@router.post("/chat")
async def urbanmind_chat(payload: ChatRequest):
    try:
        messages = [
            {"role": "system", "content": urbanmind_system_prompt}
        ]

        for msg in payload.chat_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": payload.message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        reply = response.choices[0].message.content

        quick_actions = generate_quick_actions(payload.message)

        return {
            "status": "success",
            "data": {
                "assistant_message": reply,
                "quick_actions": quick_actions,
                "detected_intents": []
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

def generate_quick_actions(user_message: str):
    """Generate relevant quick actions based on user message"""
    message_lower = user_message.lower()

    base_actions = [
        {"action": "documents", "label": "Help with documents", "section": "/official"},
        {"action": "housing", "label": "Find housing", "section": "/housing"},
        {"action": "language", "label": "Language learning", "section": "/language"},
        {"action": "community", "label": "Community events", "section": "/cultural"}
    ]

    # Check for specific intents and add relevant actions
    if any(word in message_lower for word in ['cv', 'resume', 'curriculum']):
        return [
            {"action": "cv_help", "label": "Improve my CV", "section": "/neurohr"},
            {"action": "find_jobs", "label": "Find jobs", "section": "/jobs"},
            {"action": "documents", "label": "Help with documents", "section": "/official"},
            {"action": "language", "label": "Language learning", "section": "/language"}
        ]
    elif any(word in message_lower for word in ['job', 'work', 'employment']):
        return [
            {"action": "find_jobs", "label": "Find jobs", "section": "/jobs"},
            {"action": "cv_help", "label": "Improve my CV", "section": "/neurohr"},
            {"action": "language", "label": "Language learning", "section": "/language"},
            {"action": "documents", "label": "Help with documents", "section": "/official"}
        ]
    elif any(word in message_lower for word in ['language', 'learn', 'speak', 'english']):
        return [
            {"action": "language", "label": "Language learning", "section": "/language"},
            {"action": "translation", "label": "Translation help", "section": "/translation"},
            {"action": "community", "label": "Community events", "section": "/cultural"},
            {"action": "documents", "label": "Help with documents", "section": "/official"}
        ]

    return base_actions