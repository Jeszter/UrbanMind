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
    except Exception:
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
    except Exception:
        return {"country_code": "", "country_name": "Unknown", "city": ""}


def ask_ai_for_housing_sites(location_text: str, ui_language: str) -> List[Dict[str, Any]]:
    system_prompt = """
You are an expert housing-market assistant. Given the user's location (city, region, country), return the best relevant online long-term housing and rental websites.

Rules:
- Prefer long-term and mid-term rentals.
- Avoid purely short-stay hotel sites.
- Use city-specific or national portals.
- Suggest 3–10 websites.
- Output strictly valid JSON array.
"""

    user_prompt = (
        f"User location: {location_text}\n"
        f"Language for descriptions: {ui_language}\n"
        "Return JSON array only with fields: name, url, description, country_or_region, primary_language."
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

    result = []
    for item in data:
        if isinstance(item, dict) and item.get("name") and item.get("url"):
            result.append(
                {
                    "name": item.get("name", "").strip(),
                    "url": item.get("url", "").strip(),
                    "description": item.get("description", "").strip(),
                    "country_or_region": item.get("country_or_region", "").strip(),
                    "primary_language": item.get("primary_language", "").strip(),
                }
            )

    return result


def get_cache(key: str):
    entry = CACHE.get(key)
    if entry and entry["expires"] > time.time():
        return entry["data"]
    return None


def set_cache(key: str, data: Dict[str, Any]):
    CACHE[key] = {"data": data, "expires": time.time() + CACHE_TTL}


@router.post("/get_housing_sites")
async def get_housing_sites(req: LocationRequest, request: Request):
    ui_lang = req.language or "en"

    if req.latitude and req.longitude:
        geo = reverse_geocode(req.latitude, req.longitude)
    elif req.country_code:
        geo = {
            "country_code": req.country_code.lower(),
            "country_name": req.country_code.upper(),
            "city": "",
        }
    else:
        ip = request.client.host
        geo = geolocate_ip(ip)

    country_code = geo["country_code"]
    country_name = geo["country_name"]
    city = geo["city"]

    if not country_code:
        raise HTTPException(status_code=400, detail="Cannot determine location")

    location_text = (
        f"{city}, {country_name} ({country_code.upper()})"
        if city
        else f"{country_name} ({country_code.upper()})"
    )

    cache_key = f"{country_code}:{city}:{ui_lang}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    sites = ask_ai_for_housing_sites(location_text, ui_lang)

    response = {
        "country_code": country_code,
        "country_name": country_name,
        "city": city,
        "location_text_used": location_text,
        "sites": sites,
    }

    set_cache(cache_key, response)
    return response
