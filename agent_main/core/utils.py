import json


def clean_json_response(response_text: str):
    cleaned = response_text.strip()
    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    return json.loads(cleaned.strip())
