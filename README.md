# Lecture 7: A Database Is a Machine at an Address

Aarav's plan survives a refresh and a redeploy. The page that serves it is nothing but HTML, CSS and two fetches.

**Principle:** a database is a machine at an address. SQL is its package.

| Step | Files | Adds | Lesson |
|---|---|---|---|
| 01 | `01-leak/index.html` | Browser calls Groq directly | The key shows in the Network tab |
| 02 | `02-function/diagnose.py` | Just the function, in the terminal | The process was never the UI |
| 03 | `03-fastapi/api/index.py` | The function behind FastAPI, on Vercel | The key moves to your server |
| 04 | `04-gradio-client/app.py` | Gradio calls the server, no key | The client only asks |
| 05 | `05-memory-txt/api/index.py` | Plans saved to `memory.txt` | 500 on Vercel: read-only file system |
| 06 | `06-schema/schema.sql` | `create table` from the L6 model | The machine needs a shape |
| 07 | `07-supabase-sdk/` | Insert and select through the SDK, then without it | The SDK hides the URL and headers |
| 08 | `08-supabase-api/` | The server saves rows, and a plain page replaces Gradio | Survives refreshes and redeploys, no key in the browser |

**Steps 01–05 need no database.** They only need `GROQ_API_KEY`. Supabase starts at step 06.

## Setup

```bash
pip install fastapi uvicorn requests python-dotenv gradio "supabase>=2.33" httpie
npm i -g vercel && vercel login
cp .env.example .env          # GROQ_API_KEY is enough until step 06
set -a; source .env; set +a
```

Every Python step reads its keys from the root `.env` itself with `load_dotenv`. The `source` line is only for the shell commands below, such as `http` and `vercel env add`, that use `$GROQ_API_KEY` and friends.

On Vercel there is no `.env`, so `load_dotenv` does nothing and the variables you add with `vercel env add` are used instead. The code is identical in both places.

## 01 · The leak

Paste a key into `01-leak/index.html`, open it, then Inspect → Network → send. The `Authorization` header shows the key. Whose machine? Whose key?

## 02 · Just the function

```bash
python 02-function/diagnose.py
```

## 03 · Put it on your server

Locally:

```bash
cd 03-fastapi
uvicorn api.index:app --reload
http POST :8000/api/diagnose workflow="I edit until Sunday"
```

In production:

```bash
vercel link
printf %s "$GROQ_API_KEY" | vercel env add GROQ_API_KEY production --force
vercel --prod
http POST https://<app>.vercel.app/api/diagnose workflow="I edit until Sunday"
```

| Dial | Value |
|---|---|
| Address | `127.0.0.1:8000/api/diagnose` locally, `<app>.vercel.app/api/diagnose` live |
| Action | POST |
| Key | none today (L8) |
| Package | `{"workflow"}` in, `{"plan"}` out |

Vercel finds the FastAPI `app` in `api/index.py` on its own, so there is no `vercel.json`. `--force` lets you run the env command again without an "already exists" error.

## 04 · Gradio becomes a client

With the step 03 server running locally:

```bash
python 04-gradio-client/app.py
```

Then point it at the live server, with no code change:

```bash
API_URL=https://<app>.vercel.app/api/diagnose python 04-gradio-client/app.py
```

The key lives on the machine that spends the money. Gradio never sees it.

## 05 · The file dies

```bash
cd 05-memory-txt
uvicorn api.index:app --reload
http POST :8000/api/diagnose workflow="one"
http :8000/api/plans
```

Locally it works. Deploy it and POST again: **500, read-only file system**. Locally, two simultaneous POSTs both return 200, but only one plan is saved.

A real store must survive the server being thrown away, take many writers, and answer "every plan for workflow 1, oldest first".

Local runs write to `memory.txt`. Run `git checkout 05-memory-txt/memory.txt` to empty it before class.

## 06 · Give the machine a shape

Create a Supabase project and add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` to `.env`, then run the `source` line from Setup again. A POST before any table exists fails with `relation does not exist`:

```bash
http POST $SUPABASE_URL/rest/v1/diagnoses apikey:$SUPABASE_SERVICE_KEY \
  "Authorization:Bearer $SUPABASE_SERVICE_KEY" workflow_id:=1 plan="Batch your edits." tone=plain
```

Run `06-schema/schema.sql` in the SQL editor, then POST again: 201.

| SQL | L6 model |
|---|---|
| `create table` | block → table |
| column | fact |
| `primary key` | key |
| `references` | pointer |
| `default now()` | the `memory.txt` timestamp |

## 07 · The cushion

```bash
python 07-supabase-sdk/sdk.py
python 07-supabase-sdk/rest.py
```

`sdk.py` makes the same calls as the httpie request above. The SDK hides the URL and the headers.

`rest.py` puts them back. It inserts, selects, updates and deletes a row with plain `requests`, so you can see what the SDK sends. Every table gets a URL, `{SUPABASE_URL}/rest/v1/{table}`, and filters go in the query string, such as `workflow_id=eq.1`.

The REST API only works with rows. Creating tables still happens in the SQL editor.

## 08 · The server remembers, and the page replaces Gradio

Locally, one server serves the page and the API:

```bash
cd 08-supabase-api
uvicorn api.index:app --reload
open http://127.0.0.1:8000
```

In production:

```bash
vercel link
while IFS== read -r k v; do printf %s "$v" | vercel env add "$k" production --force; done < ../.env
vercel --prod
http https://<app>.vercel.app/api/workflows/1/diagnoses
```

The page in `public/index.html` POSTs to `/api/diagnose` and lists saved plans from `/api/workflows/1/diagnoses`. Both paths are relative, so the same page works on `127.0.0.1:8000` and on `<app>.vercel.app`.

- **Locally,** FastAPI serves `public/` because the folder exists next to `api/`.
- **On Vercel,** the CDN serves `public/` and sends every other path to FastAPI.

The page and the API share one origin, so there's no CORS. Opening the page from another port, such as Live Server on 5500, makes it a different origin, and the browser blocks the call. In Network, every request goes to your own URL, and none carries a key.

`workflow_id = 1` is hardcoded on purpose; L8 fixes it. The service key stays in server env vars only.

## Done equals

A classmate opens your URL, gets a plan, refreshes, and the plan is still in the saved list. They search the network tab and find no key.

## Flags

- Vercel: the file system is read-only except `/tmp`. The first call after idle is slower. Logs for a 500 are under the deployment's Logs tab.
- Vercel: `vercel env add` only sets production here. Preview deploys without `--prod` won't have the keys.
- Supabase: free projects pause after 7 idle days. `sb_secret_` keys need `supabase>=2.33`.
- Groq: 30 requests per minute on the free tier, so a full class can hit a 429. The page shows the error instead of a blank plan. Model: `openai/gpt-oss-120b`.
