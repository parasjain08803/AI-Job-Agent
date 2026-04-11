import difflib
import asyncio
import re
from playwright.async_api import async_playwright
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

playwright = None
browser = None
context = None

INTERNHALA_PROFILES = [
    "Data Science", "Machine Learning", "Artificial Intelligence (AI)",
    "Web Development", "Full Stack Development", "Front End Development",
    "Backend Development", "Software Development", "Software Testing",
    "Python/Django Development", "Java Development", "Javascript Development",
    "Node.js Development", "PHP Development", ".NET Development", "ASP.NET Development",

    "Cloud Computing", "Cyber Security", "Blockchain Development",
    "DevOps", "MLOps Engineering", "Computer Vision",
    "Natural Language Processing (NLP)", "Big Data", "Analytics",

    "Android App Development", "iOS App Development", "Mobile App Development",
    "Flutter Development",

    "Computer Science", "Information Technology", "Database Building",

    "Digital Marketing", "SEO", "Social Media Marketing",
    "Marketing", "Sales", "Finance", "Human Resources (HR)",
    "Content Writing", "Copywriting", "Creative Writing",

    "UI/UX Design", "Graphic Design", "Video Editing",
    "Photography", "Film Making", "Motion Graphics",

    "Teaching", "Customer Service", "Operations",
    "Project Management", "Product Management",
]


async def get_browser():
    global playwright, browser, context

    if browser is None:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()

        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = await browser.new_context()

    return context

def normalize(text):
    return re.sub(r'[^a-z0-9 ]', '', text.lower())


def map_query_to_profile(query):
    query = normalize(query)

    keyword_map = {
        "ml": "Machine Learning",
        "ai": "Artificial Intelligence (AI)",
        "data": "Data Science",
        "frontend": "Front End Development",
        "backend": "Backend Development",
        "fullstack": "Full Stack Development",
        "react": "Front End Development",
        "node": "Node.js Development",
        "django": "Python/Django Development",
        "python": "Python/Django Development",
    }

    for key, value in keyword_map.items():
        if key in query:
            return value

    for profile in INTERNHALA_PROFILES:
        if query == normalize(profile):
            return profile

    for profile in INTERNHALA_PROFILES:
        if query in normalize(profile) or normalize(profile) in query:
            return profile

    matches = difflib.get_close_matches(
        query,
        [normalize(p) for p in INTERNHALA_PROFILES],
        n=1,
        cutoff=0.6
    )

    if matches:
        for profile in INTERNHALA_PROFILES:
            if normalize(profile) == matches[0]:
                return profile

    return "Software Development"



def clean_text(text):
    return text.replace("\n", "").strip() if text else ""


def remove_duplicates(jobs):
    seen = set()
    unique = []

    for job in jobs:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique.append(job)

    return unique


def slugify(profile):
    return re.sub(r'[^a-z0-9]+', '-', profile.lower()).strip('-')



async def fetch_description(url):
    try:
        page = await context.new_page()

        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0"
        })

        await page.route("**/*", lambda route: route.abort()
            if route.request.resource_type in ["image", "stylesheet", "font"]
            else route.continue_())

        await page.goto(url, timeout=15000, wait_until="domcontentloaded")

        await page.wait_for_selector(".text-container", timeout=5000)

        full_desc = ""

        about = await page.query_selector("div.text-container")
        if about:
            full_desc += await about.inner_text()

        skills = await page.query_selector_all("span.round_tabs")
        if skills:
            skill_text = " ".join([await s.inner_text() for s in skills])
            full_desc += "\nSkills: " + skill_text

        await page.close()
        return full_desc.strip()

    except Exception as e:
        print("Scraping error:", e)
        return ""


async def fetch_internshala(
    query="Software Development",
    location=None,
    remote=False,
    pages=1,
    job_type="Fresher"
):

    profile = map_query_to_profile(query)
    jobs = []

    page = await context.new_page()   # ✅ global context use

    await page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0"
    })

    await page.route("**/*", lambda route: route.abort()
        if route.request.resource_type in ["image", "stylesheet", "font"]
        else route.continue_())

    for i in range(1, pages + 1):

        if job_type == "Internship":
            if remote:
                url = f"https://internshala.com/internships/work-from-home-{slugify(profile)}-internships/page-{i}/"
            elif location:
                url = f"https://internshala.com/internships/{slugify(profile)}-internship-in-{location.lower()}/page-{i}/"
            else:
                url = f"https://internshala.com/internships/{slugify(profile)}-internship/page-{i}/"

        elif job_type == "Fresher":
            if remote:
                url = f"https://internshala.com/fresher-jobs/{slugify(profile)}-jobs/work-from-home/page-{i}/"
            elif location:
                url = f"https://internshala.com/fresher-jobs/{slugify(profile)}-jobs-in-{location.lower()}/page-{i}/"
            else:
                url = f"https://internshala.com/fresher-jobs/{slugify(profile)}-jobs/page-{i}/"

        elif job_type == "Senior":
            if remote:
                url = f"https://internshala.com/jobs/{slugify(profile)}-jobs/work-from-home/experience-2/page-{i}/"
            elif location:
                url = f"https://internshala.com/jobs/{slugify(profile)}-jobs-in-{location.lower()}/experience-2/page-{i}/"
            else:
                url = f"https://internshala.com/jobs/{slugify(profile)}-jobs/experience-2/page-{i}/"

        print(url)        

        await page.goto(url, timeout=10000, wait_until="domcontentloaded")

        await page.wait_for_selector(".individual_internship", timeout=5000)

        cards = await page.query_selector_all(".individual_internship")

        for card in cards:
            title_el = await card.query_selector(".job-internship-name")
            company_el = await card.query_selector(".company-name")
            location_el = await card.query_selector(".locations")
            link_el = await card.query_selector("a")

            title = clean_text(await title_el.inner_text()) if title_el else ""
            company = clean_text(await company_el.inner_text()) if company_el else ""
            location = clean_text(await location_el.inner_text()) if location_el else ""
            link = await link_el.get_attribute("href") if link_el else ""

            if not title or not company or not link:
                continue

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "description": None,
                "url": "https://internshala.com" + link,
                "source": "internshala",
                "type": job_type.lower(),
                "remote": "work-from-home" in link.lower()
            })
    await page.close()    

    jobs = remove_duplicates(jobs)

    return jobs

async def safe_fetch_internshala(query, location, job_type, remote):
    try:
        return await fetch_internshala(
            query=query,
            location=location,
            remote=remote,
            job_type=job_type or "Fresher"
        )
    except Exception as e:
        print("Internshala error:", e)
        return []