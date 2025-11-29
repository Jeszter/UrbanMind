import os
import io
import hashlib
import json
import time
from typing import Optional
from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from .resume_generator import analyze_cv_text, get_missing_info_prompt, generate_resume_pdf

load_dotenv()

router = APIRouter()

CACHE = {}
CACHE_TTL = 3600


class ResumeMissingRequest(BaseModel):
    cv_text: str
    language: Optional[str] = "English"


class ResumeGenerateRequest(BaseModel):
    cv_text: str
    extra_info: str = ""
    format: str = "europass"
    language: Optional[str] = "English"
    filename: Optional[str] = "resume.pdf"


def normalize_text(text: str) -> str:
    return " ".join(text.replace("\x00", "").split())


def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_text_from_file(filename: str, data: bytes) -> str:
    name_lower = filename.lower()
    if name_lower.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    if name_lower.endswith(".pdf"):
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if not text:
            raise HTTPException(status_code=400, detail="Cannot extract text from PDF.")
        return text
    if name_lower.endswith(".docx"):
        import docx
        doc = docx.Document(io.BytesIO(data))
        text = "\n".join(p.text for p in doc.paragraphs)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Cannot extract text from DOCX.")
        return text
    raise HTTPException(status_code=400, detail="Unsupported file type.")


def cache_get(key: str):
    entry = CACHE.get(key)
    if not entry:
        return None
    if entry["expires"] < time.time():
        return None
    return entry["value"]


def cache_set(key: str, value: dict):
    CACHE[key] = {"value": value, "expires": time.time() + CACHE_TTL}


@router.post("/analyze")
async def analyze_cv(file: UploadFile = File(...)):
    filename = file.filename or "file"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    data = await file.read()

    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large.")

    cv_text = extract_text_from_file(filename, data)
    cv_text = normalize_text(cv_text)

    if len(cv_text) < 100:
        raise HTTPException(status_code=400, detail="CV text too short.")

    h = get_hash(cv_text)
    cached = cache_get(h)

    if cached:
        return JSONResponse(cached)

    try:
        analysis_text = analyze_cv_text(cv_text)
        result = {
            "status": "success",
            "filename": filename,
            "analysis": analysis_text,
            "cv_text": cv_text,
        }
        cache_set(h, result)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NeuroHR error: {str(e)}")


@router.post("/resume/missing")
async def resume_missing(payload: ResumeMissingRequest):
    cv_text = normalize_text(payload.cv_text.strip())
    language = payload.language

    if len(cv_text) < 100:
        raise HTTPException(status_code=400, detail="CV text too short.")

    try:
        message = get_missing_info_prompt(cv_text, language)
        return JSONResponse({"status": "success", "message": message})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NeuroHR error: {str(e)}")


@router.post("/resume/generate")
async def resume_generate(payload: ResumeGenerateRequest):
    cv_text = normalize_text(payload.cv_text.strip())
    extra_info = payload.extra_info.strip()
    filename = payload.filename

    if len(cv_text) < 50:
        raise HTTPException(status_code=400, detail="CV text too short.")

    try:
        pdf_buffer = generate_resume_pdf(cv_text, extra_info, payload.format, payload.language)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NeuroHR error: {str(e)}")
