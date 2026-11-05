import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.ai_routes import router as ai_router
from api.demo_routes import router as demo_router
from api.resident_routes import router as resident_router
from api.review_routes import router as review_router
from api.skill_routes import router as skill_router
from api.staff_routes import router as staff_router

app = FastAPI(title="Carryover")

default_origins = "http://localhost:5173,http://127.0.0.1:5173"
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", default_origins).split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)
app.include_router(demo_router)
app.include_router(review_router)
app.include_router(skill_router)
app.include_router(staff_router)
app.include_router(resident_router)  # GET /tasks, GET /today, POST /event


@app.get("/health")
def health():
    return {"status": "ok"}
