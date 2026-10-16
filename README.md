# Lecture 7: A Database Is a Machine at an Address

Aarav's plan survives a refresh and a redeploy. The page that serves it is nothing but HTML, CSS and one fetch.

**Principle:** a database is a machine at an address. SQL is its package.

| Step | Files | Adds | Lesson |
|---|---|---|---|
| 01 | `01-leak/index.html` | Browser calls Groq directly | The key shows in the Network tab |
| 02 | `02-function/diagnose.py` | Just the function, in the terminal | The process was never the UI |
| 03 | `03-fastapi/api/index.py` | The function behind FastAPI, on Vercel | The key moves to your server |
| 04 | `04-gradio-client/app.py` | Gradio calls the live URL, no key | The client only asks |
| 05 | `05-memory-txt/api/index.py` | Plans saved to `memory.txt` | 500 on Vercel: read-only file system |
| 06 | `06-schema/schema.sql` | `create table` from the L6 model | The machine needs a shape |
| 07 | `07-supabase-sdk/sdk.py` | Insert and select through the SDK | The SDK hides the URL and headers |
| 08 | `08-supabase-api/api/index.py` | The server inserts and selects rows | Survives redeploys |
| 09 | `09-html-client/public/index.html` | One fetch replaces Gradio | No key in the browser |

**Steps 01–05 need no database.** They only need `GROQ_API_KEY`. Supabase starts at step 06.

## Setup

```bash
pip install fastapi uvicorn requests gradio "supabase>=2.33" httpie
npm i -g vercel && vercel login
cp .env.example .env          # GROQ_API_KEY is enough until step 06
set -a; source .env; set +a
```

## 01 · The leak

Paste a key into `01-leak/index.html`, open it, then Inspect → Network → send. The `Authorization` header shows the key. Whose machine? Whose key?

## 02 · Just the function

```bash
python 02-function/diagnose.py
```

## 03 · Put it on your server

```bash
cd 03-fastapi
uvicorn api.index:app --reload
http POST :8000/api/diagnose workflow="I edit until Sunday"

vercel link
printf %s "$GROQ_API_KEY" | vercel env add GROQ_API_KEY production
vercel --prod
```

| Dial | Value |
|---|---|
| Address | `<app>.vercel.app/api/diagnose` |
| Action | POST |
| Key | none today (L8) |
| Package | `{"workflow"}` in, `{"plan"}` out |

To try the step 09 page now, without a database, run `cp -r ../09-html-client/public .` and then `vercel --prod`.

## 04 · Gradio becomes a client

Set `URL` in `04-gradio-client/app.py` to your live URL and run it locally. The key lives on the machine that spends the money.

## 05 · The file dies

```bash
cd 05-memory-txt
uvicorn api.index:app --reload
http POST :8000/api/diagnose workflow="one"
http :8000/api/plans
```

Locally it works. Deploy it and POST again: **500, read-only file system**. Locally, two simultaneous POSTs both return 200, but only one plan is saved.

A real store must survive the server being thrown away, take many writers, and answer "every plan for workflow 1, oldest first".

## 06 · Give the machine a shape

Create a Supabase project and add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` to `.env`. A POST before any table exists fails with `relation does not exist`:

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
```

These are the same calls as the httpie request above. The SDK hides the URL and the headers.

## 08 · The server remembers

```bash
cd 08-supabase-api
vercel link
while IFS== read -r k v; do printf %s "$v" | vercel env add "$k" production; done < ../.env
vercel --prod
http https://<app>.vercel.app/api/workflows/1/diagnoses
```

`workflow_id = 1` is hardcoded on purpose; L8 fixes it. The service key stays in server env vars only.

## 09 · Rip off Gradio

```bash
cp -r 09-html-client/public 08-supabase-api/
cd 08-supabase-api && vercel --prod
```

The page and the API share one origin, so there's no CORS. In Network, the only request goes to your URL, and it carries no key.

## Done equals

A classmate opens your URL, gets a plan, refreshes, and the plan is still there. They search the network tab and find no key.

## Flags

- Vercel: the file system is read-only except `/tmp`. The first call after idle is slower.
- Supabase: free projects pause after 7 idle days. `sb_secret_` keys need `supabase>=2.33`.
- Groq: 30 requests per minute on the free tier. Model: `openai/gpt-oss-120b`.
