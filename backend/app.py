from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import resume
from routes import job
from routes import apply

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(resume.router)
app.include_router(job.router)
app.include_router(apply.router)

@app.get("/")
def home():
    return {"message":"AI job agent is running"}



