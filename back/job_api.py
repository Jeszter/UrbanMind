import os
import json
import requests
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()


class LocationRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: Optional[str] = None
    language: Optional[str] = None


def reverse_geocode(lat: float, lon: float) -> Dict[str, str]:
    try:
        url = (
            f"https://nominatim.openstreetmap.org/reverse?"
            f"lat={lat}&lon={lon}&format=json&addressdetails=1"
        )
        resp = requests.get(url, headers={"User-Agent": "UrbanMind/1.0"}, timeout=10)
        data = resp.json()
        addr = data.get("address", {})
        return {
            "country_code": addr.get("country_code", "").lower(),
            "country_name": addr.get("country", "") or "Unknown",
            "city": addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("municipality")
            or addr.get("state")
            or "",
        }
    except Exception:
        return {"country_code": "", "country_name": "Unknown", "city": ""}


def geolocate_ip(ip: str) -> Dict[str, str]:
    try:
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=8)
        data = resp.json()
        code = str(data.get("country_code", "")).lower()
        country_name = data.get("country_name", "") or "Unknown"
        city = data.get("city", "") or data.get("region", "") or ""
        return {
            "country_code": code,
            "country_name": country_name,
            "city": city,
        }
    except Exception:
        return {"country_code": "", "country_name": "Unknown", "city": ""}


def ask_ai_for_job_sites(location_text: str, ui_language: str) -> List[Dict[str, Any]]:
    system_prompt = """
You are an expert career advisor and job-market analyst.

Given the user's location (which may include city, region and country), recommend the most relevant, popular and trustworthy ONLINE JOB SEARCH WEBSITES for that specific area.

Rules:
- Always pay attention to the CITY if it is provided. Prefer city-specific or regional job portals and boards first, then add the most important national platforms.
- Suggest 3–10 websites.
- Include only real and plausible job boards, career portals, or official public employment services.
- Do not include social media profiles, generic discussion forums, Telegram channels, Discord servers, or obviously unrelated websites.
- If the city is smaller and there are no known local-only job boards, combine:
  - the nearest big-city or regional portals, and
  - the main national job portals widely used in that country.
- Be realistic and up to date, but do not invent obviously fake brands.

Output:
- Output MUST be valid JSON only, with no extra text.
- Use this JSON schema:

[
  {
    "name": "string",
    "url": "string",
    "description": "short string (1–2 sentences, may include which roles or sectors the site is best for)",
    "country_or_region": "string",
    "primary_language": "string",
    "focus_area": "string"
  }
]
"""
    user_prompt = (
        f"User interface language: {ui_language}.\n"
        f"User location: {location_text}.\n\n"
        "Return ONLY a JSON array following the schema. "
        "Descriptions may be in the UI language or English."
    )

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
        if isinstance(data, list):
            cleaned = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "")).strip()
                url = str(item.get("url", "")).strip()
                if not name or not url:
                    continue
                cleaned.append(
                    {
                        "name": name,
                        "url": url,
                        "description": str(item.get("description", "")).strip(),
                        "country_or_region": str(
                            item.get("country_or_region", "")
                        ).strip(),
                        "primary_language": str(
                            item.get("primary_language", "")
                        ).strip(),
                        "focus_area": str(item.get("focus_area", "")).strip(),
                    }
                )
            return cleaned
        return []
    except json.JSONDecodeError:
        return []


@router.post("/api/get_job_sites")
async def get_job_sites(req: LocationRequest, request: Request):
    ui_lang = req.language or "en"
    country_code = ""
    country_name = ""
    city = ""

    if req.latitude is not None and req.longitude is not None:
        geo = reverse_geocode(req.latitude, req.longitude)
        country_code = geo.get("country_code", "")
        country_name = geo.get("country_name", "Unknown")
        city = geo.get("city", "")
    elif req.country_code:
        country_code = req.country_code.lower()
        country_name = req.country_code.upper()
        city = ""
    else:
        client_ip = request.client.host
        geo = geolocate_ip(client_ip)
        country_code = geo.get("country_code", "")
        country_name = geo.get("country_name", "Unknown")
        city = geo.get("city", "")

    if not country_code and not country_name and not city:
        raise HTTPException(status_code=400, detail="Location not provided and IP lookup failed")

    if city:
        location_text = f"{city}, {country_name} ({country_code.upper()})"
    else:
        location_text = f"{country_name} ({country_code.upper()})"

    sites = ask_ai_for_job_sites(location_text, ui_lang)

    return {
        "country_code": country_code or "unknown",
        "country_name": country_name or "Unknown",
        "city": city,
        "location_text_used": location_text,
        "sites": sites,
    }
