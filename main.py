import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from back.work_backend import router as work_router
from back.docs_backend import router as docs_router
from back.language_backend import router as language_router
from back.housing_backend import router as housing_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(work_router, prefix="/work")
app.include_router(docs_router, prefix="/docs")
app.include_router(language_router, prefix="/language")
app.include_router(housing_router, prefix="/housing")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
