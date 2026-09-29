import json
import os
import time

from dotenv import load_dotenv
from google import genai

from prompts import EVALUATION_PROMPT

load_dotenv()

MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]

WEIGHTS = {
    "accuracy": 0.25,
    "relevance": 0.20,
    "completeness": 0.15,
    "clarity": 0.10,
    "instruction_following": 0.20,
    "safety": 0.10,
}


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.startswith("your"):
        raise ValueError("Gemini API key missing. Add it to your .env file.")
    return genai.Client(api_key=api_key)


def calculate_overall_score(result: dict) -> float:
    total = sum(result[name] * weight for name, weight in WEIGHTS.items())
    return round(total, 1)


def get_decision(score: float) -> str:
    if score >= 85:
        return "PASS"
    if score >= 70:
        return "HUMAN REVIEW"
    return "FAIL"


def evaluate_response(original_prompt: str, ai_response: str, reference_answer: str = "") -> dict:
    user_content = (
        EVALUATION_PROMPT
        + "\n\nOriginal User Prompt:\n" + original_prompt
        + "\n\nAI Generated Response:\n" + ai_response
        + "\n\nReference Answer (may be empty):\n" + (reference_answer or "None provided")
    )

    client = get_client()
    response = None
    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_content,
                    config={"response_mime_type": "application/json"},
                )
                break
            except Exception as error:
                last_error = error
                if "503" in str(error) or "429" in str(error):
                    time.sleep(3)
                    continue
                if "404" in str(error):
                    break
                raise
        if response is not None:
            break

    if response is None:
        raise last_error

    try:
        result = json.loads(response.text)
        for name in WEIGHTS:
            result[name] = max(0, min(100, int(result[name])))
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        raise ValueError("The AI returned an unexpected format. Please try again.")

    result["overall_score"] = calculate_overall_score(result)
    result["decision"] = get_decision(result["overall_score"])
    return result