import os
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

work_system_prompt = """
You are an AI assistant for migrants focused on work and education.
Always respond in the same language as the user's last message.
Provide clear, practical advice and structured answers.
If you are unsure about country-specific legal details, say that your advice is general and should be verified on official resources.
"""

resume_system_prompt = """
You are a professional CV and resume writer with experience adapting resumes to local job markets.
Always write in the language specified by the user and produce a full, structured resume.
Do not add fake contact details; use placeholders when necessary.
Make the candidate look professional and realistic based on the provided information.
"""

class WorkChatRequest(BaseModel):
    message: str

class ResumeRequest(BaseModel):
    profile: str
    target_language: str

@router.post("/chat")
async def work_chat(data: WorkChatRequest):
    message = data.message.strip()
    if not message:
        return JSONResponse({"status": "error", "message": "Message is empty."}, status_code=400)
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": work_system_prompt},
                {"role": "user", "content": message},
            ],
        )
        reply = response.choices[0].message.content
        return JSONResponse({"status": "success", "reply": reply})
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Work chat error: {str(e)}"}, status_code=500)

@router.post("/generate-resume")
async def generate_resume(data: ResumeRequest):
    profile = data.profile.strip()
    target_language = data.target_language.strip()
    if not profile or not target_language:
        return JSONResponse(
            {"status": "error", "message": "Missing 'profile' or 'target_language'."},
            status_code=400,
        )
    try:
        prompt = (
            f"Target language: {target_language}\n"
            f"User profile:\n{profile}\n\n"
            f"Generate a complete resume in the target language. Return only the resume."
        )
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": resume_system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        resume_text = response.choices[0].message.content
        return JSONResponse(
            {
                "status": "success",
                "resume": resume_text,
                "language": target_language,
            }
        )
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": f"Resume generation error: {str(e)}"},
            status_code=500,
        )
