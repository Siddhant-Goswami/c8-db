import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PROMPT = "Diagnose this creator workflow and give a short numbered plan:\n\n"


def diagnose(workflow: str) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": PROMPT + workflow}]},
    )
    r.raise_for_status()  # a Groq error, such as a 429 rate limit, shows by name in the logs
    return r.json()["choices"][0]["message"]["content"]


print(diagnose(input("Workflow: ")))
