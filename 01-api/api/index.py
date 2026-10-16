import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

PROMPT = "Diagnose this creator workflow and give a short numbered plan:\n\n"


def diagnose(workflow: str) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": PROMPT + workflow}]},
    )
    return r.json()["choices"][0]["message"]["content"]


app = FastAPI()


class WorkflowIn(BaseModel):
    workflow: str


@app.post("/api/diagnose")
def diagnose_route(body: WorkflowIn):
    return {"plan": diagnose(body.workflow)}
