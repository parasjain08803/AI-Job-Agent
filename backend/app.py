import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import resume
from routes import job
from routes import apply
from routes import analysis

from services.internshala_job_scrapping import get_browser


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-job-agent-virid.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(resume.router)
app.include_router(job.router)
app.include_router(apply.router)
app.include_router(analysis.router)



from services.internshala_job_scrapping import browser, playwright

@app.on_event("shutdown")
async def shutdown_event():
    if browser:
        await browser.close()
    if playwright:
        await playwright.stop()
    print("🛑 Playwright browser closed")


@app.get("/")
def home():
    return {"message": "AI job agent is running"}