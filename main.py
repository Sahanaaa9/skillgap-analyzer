from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import employees, skills, auth, ai

app = FastAPI(
    title="SkillGap Analyzer API",
    description="AI-powered workforce skill gap analysis for small businesses",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(skills.router)
app.include_router(ai.router)

@app.get("/")
def root():
    return {
        "app": "SkillGap Analyzer API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
