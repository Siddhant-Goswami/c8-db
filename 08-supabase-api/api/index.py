import os

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client

PROMPT = "Diagnose this creator workflow and give a short numbered plan:\n\n"

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


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
    plan = diagnose(body.workflow)
    supabase.table("diagnoses").insert({"workflow_id": 1, "plan": plan, "tone": "plain"}).execute()
    return {"plan": plan}


@app.get("/api/workflows/{workflow_id}/diagnoses")
def list_diagnoses(workflow_id: int):
    return supabase.table("diagnoses").select("*") \
        .eq("workflow_id", workflow_id).order("created_at").execute().data


@app.post("/api/roll")
def roll(body: NameIn):
    supabase.table("roll").insert({"name": body.name}).execute()
    return {"name": body.name}
