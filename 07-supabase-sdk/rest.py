# The same calls as sdk.py, with no SDK: just HTTP requests to Supabase's REST API.
# Every table in your database gets a URL: {SUPABASE_URL}/rest/v1/{table}
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

URL = f"{os.environ['SUPABASE_URL']}/rest/v1/diagnoses"
KEY = os.environ["SUPABASE_SERVICE_KEY"]
HEADERS = {
    "apikey": KEY,                          # which project is calling
    "Authorization": f"Bearer {KEY}",       # what this caller is allowed to do
    "Prefer": "return=representation",      # send back the rows we changed
}

# CREATE: POST a JSON row. The database fills in id and created_at.
row = requests.post(URL, headers=HEADERS, json={"workflow_id": 1, "plan": "Batch your edits.", "tone": "plain"}).json()[0]
print("insert:", row)

# READ: GET with filters in the query string.
# eq.1 means "= 1". order=created_at.asc sorts oldest first.
rows = requests.get(URL, headers=HEADERS, params={"workflow_id": "eq.1", "order": "created_at.asc"}).json()
print("select:", len(rows), "rows for workflow 1")

# UPDATE: PATCH the rows that match the filter.
print("update:", requests.patch(URL, headers=HEADERS, params={"id": f"eq.{row['id']}"}, json={"tone": "friendly"}).json())

# DELETE: DELETE the rows that match the filter. With no filter, Supabase refuses.
print("delete:", requests.delete(URL, headers=HEADERS, params={"id": f"eq.{row['id']}"}).json())
