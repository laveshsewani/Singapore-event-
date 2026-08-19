import json
import os
from groq import Groq, RateLimitError
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EXTRACTION_PROMPT = """You will be given the raw visible text of a webpage for a \
technology event in Singapore. Extract the following fields as JSON only:

{{
  "name": "event name, or null if this isn't actually an event page",
  "date_text": "the date or date range as written on the page, or null",
  "venue": "venue name, or null",
  "organizer": "organizing company/body, or null",
  "category": "one short category like 'AI', 'Startup', 'Fintech', 'General Tech'",
  "speakers": [
    {{
      "name": "...",
      "title": "...",
      "company": "...",
      "bio_snippet": "1-2 sentence bio if present, else null",
      "linkedin_url": "only if a LinkedIn URL is literally written on the page for this person, else null",
      "company_url": "only if a company website URL is literally written on the page, else null"
    }}
  ]
}}

If the page is not actually an event detail page, set "name" to null and \
"speakers" to an empty list. Only include people explicitly listed as speakers, \
exhibitors, panelists, or founders — do not invent names or URLs. Only fill in \
linkedin_url/company_url if that exact URL text appears on the page.

PAGE TEXT:
{page_text}
"""


def extract_event(page_text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=1500,
            messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(page_text=page_text)}],
            response_format={"type": "json_object"},
        )
    except RateLimitError as e:
        print(f"extract_event: rate limited, skipping this page for now ({e})")
        return None

    raw = response.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("extract_event: could not parse output, skipping page")
        return None
    if not data.get("name"):
        return None
    return data