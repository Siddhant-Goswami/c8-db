import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

print(supabase.table("diagnoses").insert({"workflow_id": 1, "plan": "Batch your edits.", "tone": "plain"}).execute().data)
print(supabase.table("diagnoses").select("*").eq("workflow_id", 1).order("created_at").execute().data)
