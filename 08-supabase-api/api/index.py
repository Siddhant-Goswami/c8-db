import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from supabase import create_client

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

PROMPT = "Diagnose this creator workflow and give a short numbered plan output in plain text. Don't use markdown:\n\n"

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def diagnose(workflow: str) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": PROMPT + workflow}]},
    )
    r.raise_for_status()  # a Groq error, such as a 429 rate limit, shows by name in the logs
    return r.json()["choices"][0]["message"]["content"]


app = FastAPI()


class WorkflowIn(BaseModel):
    workflow: str


@app.post("/api/diagnose")
def diagnose_route(body: WorkflowIn):
    plan = diagnose(body.workflow)
    supabase.table("diagnoses").insert({"workflow_id": 1, "plan": plan, "tone": "plain"}).execute()
    return {"plan": plan}


@app.get("/api/workflows/{workflow_id}/diagnoses")
def list_diagnoses(workflow_id: int):
    return supabase.table("diagnoses").select("*") \
        .eq("workflow_id", workflow_id).order("created_at").execute().data


# Locally, serve the page from this same server so the page and the API share
# one origin, exactly like on Vercel. On Vercel, its CDN serves public/ itself.
# This mount comes last so the /api routes above are matched first.
PUBLIC = Path(__file__).resolve().parents[1] / "public"
if PUBLIC.is_dir():
    app.mount("/", StaticFiles(directory=PUBLIC, html=True), name="public")
