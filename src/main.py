from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router.routers import router
from app.ai_analysis.apis.learning_analysis_api import router as learning_analysis_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(learning_analysis_router)