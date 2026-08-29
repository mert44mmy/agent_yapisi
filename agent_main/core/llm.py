import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Create a .env file from .env.example.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)


def call_llm(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text
