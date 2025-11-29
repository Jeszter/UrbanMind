import os
import json
import time
import requests
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 60 * 60


class LocationRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: Optional[str] = None
    language: Optional[str] = None


def reverse_geocode(lat: float, lon: float) -> Dict[str, str]:
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        resp = requests.get(url, headers={"User-Agent": "UrbanMind"}, timeout=10)
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
    except:
        return {"country_code": "", "country_name": "Unknown", "city": ""}


def geolocate_ip(ip: str) -> Dict[str, str]:
    try:
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
        data = resp.json()
        return {
            "country_code": str(data.get("country_code", "")).lower(),
            "country_name": data.get("country_name", "") or "Unknown",
            "city": data.get("city", "") or data.get("region", "") or "",
        }
    except:
        return {"country_code": "", "country_name": "Unknown", "city": ""}


def ask_ai_for_job_sites(location_text: str, ui_language: str) -> List[Dict[str, Any]]:
    system_prompt = """
You are an expert job-market analyst. Given the user's location (including city, region and country), return the best relevant online job search websites.

Rules:
- Use city-specific or regional platforms when possible.
- If the city lacks known sites, choose nearest big-city portals and national portals.
- Suggest 3–10 websites.
- Only real job boards, public employment services or well-known platforms.
- Output strictly valid JSON array.
    """

    user_prompt = (
        f"User location: {location_text}\n"
        f"Language: {ui_language}\n"
        "Return JSON array only, with fields: name, url, description, country_or_region, primary_language, focus_area."
    )

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = resp.choices[0].message.content

    try:
        data = json.loads(content)
    except:
        return []

    if not isinstance(data, list):
        return []

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
                "country_or_region": str(item.get("country_or_region", "")).strip(),
                "primary_language": str(item.get("primary_language", "")).strip(),
                "focus_area": str(item.get("focus_area", "")).strip(),
            }
        )
    return cleaned


def get_cache(key: str) -> Optional[Dict[str, Any]]:
    entry = CACHE.get(key)
    if not entry:
        return None
    if entry["expires"] < time.time():
        return None
    return entry["data"]


def set_cache(key: str, data: Dict[str, Any]):
    CACHE[key] = {"data": data, "expires": time.time() + CACHE_TTL}


@router.post("/api/get_job_sites")
async def get_job_sites(req: LocationRequest, request: Request):
    ui_lang = req.language or "en"

    country_code = ""
    country_name = ""
    city = ""

    if req.latitude is not None and req.longitude is not None:
        geo = reverse_geocode(req.latitude, req.longitude)
        country_code = geo["country_code"]
        country_name = geo["country_name"]
        city = geo["city"]
    elif req.country_code:
        country_code = req.country_code.lower()
        country_name = req.country_code.upper()
        city = ""
    else:
        ip = request.client.host
        geo = geolocate_ip(ip)
        country_code = geo["country_code"]
        country_name = geo["country_name"]
        city = geo["city"]

    if not country_code and not country_name:
        raise HTTPException(status_code=400, detail="Cannot determine location")

    if city:
        location_text = f"{city}, {country_name} ({country_code.upper()})"
    else:
        location_text = f"{country_name} ({country_code.upper()})"

    cache_key = f"{country_code}:{city}:{ui_lang}"
    cached = get_cache(cache_key)

    if cached:
        return cached

    ai_sites = ask_ai_for_job_sites(location_text, ui_lang)

    response = {
        "country_code": country_code or "unknown",
        "country_name": country_name or "Unknown",
        "city": city,
        "location_text_used": location_text,
        "sites": ai_sites,
    }

    set_cache(cache_key, response)

    return response
