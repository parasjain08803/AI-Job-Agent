from chains.application_chain import application_chain
import json

def generate_application(resume_data, job):
    response = application_chain.invoke({
        "resume": resume_data,
        "job": job["description"]
    })

    content = response.content

    try:
        parsed = json.loads(content)
    except:
        # fallback if formatting is slightly wrong
        content = content.replace("```json", "").replace("```", "")
        parsed = json.loads(content)

    return {
        "title": job["title"],
        "company": job.get("company"),
        "application": parsed
    }