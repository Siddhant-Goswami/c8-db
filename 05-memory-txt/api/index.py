import os
from datetime import datetime

import requests
from fastapi import FastAPI
from pydantic import BaseModel

PROMPT = "Diagnose this creator workflow and give a short numbered plan:\n\n"


def diagnose(workflow: str) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": PROMPT + workflow}]},
    )
    return r.json()["choices"][0]["message"]["content"]


app = FastAPI()


class WorkflowIn(BaseModel):
    workflow: str


class NameIn(BaseModel):
    name: str


@app.post("/api/diagnose")
def diagnose_route(body: WorkflowIn):
    memory = open("memory.txt").read()
    plan = diagnose(body.workflow)
    line = f"{datetime.now()} | {body.workflow} | {plan}".replace("\n", " ")
    open("memory.txt", "w").write(memory + line + "\n")
    return {"plan": plan}


@app.get("/api/plans")
def plans():
    return open("memory.txt").read().splitlines()


@app.post("/api/roll")
def roll(body: NameIn):
    memory = open("memory.txt").read()
    open("memory.txt", "w").write(memory + f"{datetime.now()} | roll | {body.name}\n")
    return {"name": body.name}
