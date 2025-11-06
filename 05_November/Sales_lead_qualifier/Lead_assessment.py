from fastapi import FastAPI, Request
import requests
from bs4 import BeautifulSoup
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()

@app.post("/evaluate")
async def evaluate_lead(request: Request):
    data = await request.json()

    prompt = f"""
    You are an AI sales assistant. Evaluate this lead and score it from 0–10.

    Criteria:
    - Clarity of business problem
    - Fit with AI solutions
    - Budget and urgency
    - Industry relevance
    - Professionalism of responses

    Return valid JSON only:
    {{
      "lead_score": "",
      "lead_category": "",
      "summary": ""
    }}

    Lead details:
    Industry: {data.get("Industry")}
    Problem: {data.get("Problem")}
    Solution: {data.get("Solution")}
    Timeline: {data.get("Timeline")}
    Budget: {data.get("Budget")}
    Comments: {data.get("Comments")}
    """

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    body = {
        "model": "openai/gpt-4o-mini",
        "temperature": 0.4,
        "max_tokens": 250,
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    ai_json = response.json()

    ai_result = ai_json.get("choices", [{}])[0].get("message", {}).get("content", "")

    cleaned = re.sub(r"^```json|```$", "", ai_result.strip(), flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed = {"lead_score": None, "lead_category": None, "summary": ai_result}

    return parsed


@app.post("/scrape_website")
async def scrape_website(request: Request):
    data = await request.json()

    url = data.get("url")

    # Check if the URL is valid
    if not url or not url.startswith("http"):
        return {"error": "Invalid URL"}

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else "No title found"
        description = soup.find("meta", attrs={"name": "description"})
        description_content = description["content"] if description else "No description found"

        about_section = extract_section(soup, "about")
        mission_section = extract_section(soup, "mission")
        services_section = extract_section(soup, "services")

        company_info = ""
        if title and title != "No title found":
            company_info += title + " "
        if description_content and description_content != "No description found":
            company_info += description_content + " "
        if about_section and about_section != "Section not found.":
            company_info += about_section + " "
        if mission_section and mission_section != "Section not found.":
            company_info += mission_section + " "
        if services_section and services_section != "Section not found.":
            company_info += services_section + " "

        return {
            "company_info": company_info.strip()
        }

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}




def extract_section(soup, section_name):
    section = None
    if section_name.lower() == "about":
        section = soup.find(["h2", "h3"], string=re.compile("about", re.I))
    elif section_name.lower() == "mission":
        section = soup.find(["h2", "h3"], string=re.compile("mission", re.I))
    elif section_name.lower() == "services":
        section = soup.find(["h2", "h3"], string=re.compile("services", re.I))

    if section:
        next_elements = section.find_next_siblings()
        section_content = ""
        for elem in next_elements:
            if elem.name in ["h2", "h3"]:
                break
            section_content += elem.get_text() + " "

        return section_content.strip()

    return "Section not found."


def extract_contact_email(soup):
    contact_info = soup.find("a", href=re.compile("mailto:"))
    if contact_info:
        return contact_info["href"].replace("mailto:", "").strip()
    return "No contact email found"

