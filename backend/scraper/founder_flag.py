import json
import os
from groq import Groq, RateLimitError
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FLAG_PROMPT = """For each person below, based ONLY on the title/company/bio given \
(do not use outside knowledge about real people), assess:

1. is_founder: "yes" if their title clearly indicates founder/co-founder/CEO of a \
company they started, "no" if clearly not, "unclear" otherwise.
2. india_signal: "high" if the bio/company explicitly connects them to India, \
"medium" if there's a plausible but indirect signal (e.g. an Indian-origin name \
with no other confirming detail), "low" if barely any signal, "none" if nothing.
3. india_signal_reason: one short sentence citing the specific text used.

Be conservative — a name alone is "medium" at most, never "high".

Return ONLY a JSON object with key "results" containing an array, one object per \
person, in the same order, with fields: name, is_founder, india_signal, india_signal_reason

PEOPLE:
{people_json}
"""


def flag_founders(speakers):
    if not speakers:
        return []
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=1500,
            messages=[{"role": "user", "content": FLAG_PROMPT.format(people_json=json.dumps(speakers, indent=2))}],
            response_format={"type": "json_object"},
        )
    except RateLimitError as e:
        print(f"flag_founders: rate limited, marking unclear for now ({e})")
        return [{**s, "is_founder": "unclear", "india_signal": "none",
                  "india_signal_reason": "rate limited during flagging"} for s in speakers]

    raw = response.choices[0].message.content.strip()
    try:
        flags = json.loads(raw).get("results", [])
    except json.JSONDecodeError:
        print("flag_founders: could not parse output, marking all unclear")
        return [{**s, "is_founder": "unclear", "india_signal": "none",
                  "india_signal_reason": "flagging step failed"} for s in speakers]
    flags_by_name = {f["name"]: f for f in flags}
    enriched = []
    for s in speakers:
        f = flags_by_name.get(s["name"], {})
        enriched.append({
            **s,
            "is_founder": f.get("is_founder", "unclear"),
            "india_signal": f.get("india_signal", "none"),
            "india_signal_reason": f.get("india_signal_reason", ""),
        })
    return enriched