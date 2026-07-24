from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import router as auth_router
from app.topics import router as topics_router
from app.assignments import router as assignment_router
from app.progress import router  as progress_router

app = FastAPI(title="LMS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(topics_router)
app.include_router(assignment_router)
app.include_router(progress_router)