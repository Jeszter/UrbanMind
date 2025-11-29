import requests
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LocationRequest(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    country_code: str | None = None


COUNTRY_JOB_SITES = {
    "sk": [
        {"name": "Profesia.sk", "url": "https://www.profesia.sk/"},
        {"name": "Práca.sk", "url": "https://www.praca.sk/"},
        {"name": "LinkedIn Slovakia", "url": "https://www.linkedin.com/jobs/slovakia"},
    ],
    "cz": [
        {"name": "Jobs.cz", "url": "https://www.jobs.cz/"},
        {"name": "Prace.cz", "url": "https://www.prace.cz/"},
        {"name": "LinkedIn Czechia", "url": "https://www.linkedin.com/jobs/czechia"},
    ],
    "pl": [
        {"name": "Pracuj.pl", "url": "https://www.pracuj.pl/"},
        {"name": "OLX Praca", "url": "https://www.olx.pl/praca/"},
        {"name": "LinkedIn Poland", "url": "https://www.linkedin.com/jobs/poland"},
    ],
    "de": [
        {"name": "Indeed DE", "url": "https://de.indeed.com/"},
        {"name": "StepStone", "url": "https://www.stepstone.de/"},
        {"name": "LinkedIn Germany", "url": "https://www.linkedin.com/jobs/germany"},
    ],
    "us": [
        {"name": "Indeed USA", "url": "https://www.indeed.com/"},
        {"name": "Glassdoor", "url": "https://www.glassdoor.com/"},
        {"name": "LinkedIn USA", "url": "https://www.linkedin.com/jobs/united-states"},
    ],
    "uk": [
        {"name": "Reed", "url": "https://www.reed.co.uk/"},
        {"name": "Indeed UK", "url": "https://uk.indeed.com/"},
        {"name": "LinkedIn UK", "url": "https://www.linkedin.com/jobs/uk"},
    ],
}

def reverse_geocode(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        resp = requests.get(url, headers={"User-Agent": "UrbanMind"}).json()
        code = resp["address"]["country_code"]
        name = resp["address"]["country"]
        return code, name
    except:
        return None, None

@router.post("/api/get_job_sites")
def get_job_sites(req: LocationRequest):
    if req.country_code:
        code = req.country_code.lower()
        sites = COUNTRY_JOB_SITES.get(code, [])
        return {"country_code": code, "country_name": code.upper(), "sites": sites}

    if req.latitude and req.longitude:
        code, name = reverse_geocode(req.latitude, req.longitude)
        if code:
            sites = COUNTRY_JOB_SITES.get(code, [])
            return {"country_code": code, "country_name": name, "sites": sites}

    return {
        "country_code": "unknown",
        "country_name": "Unknown",
        "sites": []
    }
