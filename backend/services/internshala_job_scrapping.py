# backend/services/internshala_service.py
import difflib
import asyncio
import re
from playwright.async_api import async_playwright

INTERNHALA_PROFILES = [
    # Core Tech
    "Data Science", "Machine Learning", "Artificial Intelligence (AI)",
    "Web Development", "Full Stack Development", "Front End Development",
    "Backend Development", "Software Development", "Software Testing",
    "Python/Django Development", "Java Development", "Javascript Development",
    "Node.js Development", "PHP Development", ".NET Development", "ASP.NET Development",

    # Advanced Tech
    "Cloud Computing", "Cyber Security", "Blockchain Development",
    "DevOps", "MLOps Engineering", "Computer Vision",
    "Natural Language Processing (NLP)", "Big Data", "Analytics",

    # App Dev
    "Android App Development", "iOS App Development", "Mobile App Development",
    "Flutter Development",

    # Others Tech
    "Computer Science", "Information Technology", "Database Building",

    # Non-Tech
    "Digital Marketing", "SEO", "Social Media Marketing",
    "Marketing", "Sales", "Finance", "Human Resources (HR)",
    "Content Writing", "Copywriting", "Creative Writing",

    # Design & Media
    "UI/UX Design", "Graphic Design", "Video Editing",
    "Photography", "Film Making", "Motion Graphics",

    # Misc
    "Teaching", "Customer Service", "Operations",
    "Project Management", "Product Management",
]


def normalize(text):
    return re.sub(r'[^a-z0-9 ]', '', text.lower())

def map_query_to_profile(query):
    query = normalize(query)

    # 🔥 1. KEYWORD FIRST (VERY IMPORTANT)
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

    # 🔹 2. Exact match
    for profile in INTERNHALA_PROFILES:
        if query == normalize(profile):
            return profile

    # 🔹 3. Contains match
    for profile in INTERNHALA_PROFILES:
        if query in normalize(profile) or normalize(profile) in query:
            return profile

    # 🔹 4. Fuzzy match (LAST fallback)
    matches = difflib.get_close_matches(
        query,
        [normalize(p) for p in INTERNHALA_PROFILES],
        n=1,
        cutoff=0.6   # 🔥 increase cutoff (important)
    )

    if matches:
        for profile in INTERNHALA_PROFILES:
            if normalize(profile) == matches[0]:
                return profile

    return "Software Development"



# 🔹 Clean text
def clean_text(text):
    return text.replace("\n", "").strip() if text else ""


# 🔹 Deduplication
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


# 🔹 FAST description fetcher
async def fetch_description(browser, url, semaphore):
    async with semaphore:
        try:
            page = await browser.new_page()

            # ⚡ Block heavy resources
            await page.route("**/*", lambda route: route.abort()
                if route.request.resource_type in ["image", "stylesheet", "font"]
                else route.continue_())

            await page.goto(url)

            # ⚡ Smart wait (instead of fixed sleep)
            await page.wait_for_selector(".text-container", timeout=5000)

            full_desc = ""

            # 🔹 Section 1: Responsibilities
            about = await page.query_selector("div.text-container")
            if about:
                full_desc += await about.inner_text()

            # 🔹 Section 2: Skills
            skills = await page.query_selector_all("span.round_tabs")
            if skills:
                skill_text = " ".join([await s.inner_text() for s in skills])
                full_desc += "\nSkills: " + skill_text


            await page.close()
            return full_desc.strip()

        except:
            return ""        


# 🔹 MAIN SCRAPER
async def fetch_internshala(query="Software Developement",location=None, remote=False, pages=1,job_type="Fresher"):

    profile = map_query_to_profile(query)
    print(profile)
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # ⚡ Block heavy resources for listing page
        await page.route("**/*", lambda route: route.abort()
            if route.request.resource_type in ["image", "stylesheet", "font"]
            else route.continue_())

        # 🔹 Step 1: Scrape job list
        for i in range(1, pages + 1):

            if job_type == "Internship":

                if remote:
                    url = f"https://internshala.com/internships/work-from-home-{slugify(profile)}-internship/page-{i}/"

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



            await page.goto(url)

            # ⚡ Smart wait
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
                    "description": "",
                    "url": "https://internshala.com" + link,
                    "source": "Internshala",
                    "type": job_type.lower(),
                    "remote": "work-from-home" in link.lower()
                })

        # 🔹 Step 2: Deduplicate
        jobs = remove_duplicates(jobs)

        # 🔹 Step 3: Fetch descriptions (ASYNC FAST)
        semaphore = asyncio.Semaphore(8)  # 🔥 increased concurrency

        tasks = [
            fetch_description(browser, job["url"], semaphore)
            for job in jobs
        ]

        descriptions = await asyncio.gather(*tasks)

        # 🔹 Step 4: Attach descriptions
        for i, job in enumerate(jobs):
            job["description"] = descriptions[i]

        await browser.close()


    return jobs

