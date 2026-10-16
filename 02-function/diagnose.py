import os
import requests

PROMPT = "Diagnose this creator workflow and give a short numbered plan:\n\n"


def diagnose(workflow: str) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": PROMPT + workflow}]},
    )
    return r.json()["choices"][0]["message"]["content"]


print(diagnose(input("Workflow: ")))
