import json
import re

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)

    if not match:
        return None

    raw = match.group()

    raw = raw.replace("\\.env", ".env")

    try:
        return json.loads(raw)
    except Exception:
        return None