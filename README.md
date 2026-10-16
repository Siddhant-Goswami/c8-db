# Lecture 7: A Database Is a Machine at an Address

Deploy an API, try to remember with a file, watch it break, then remember with a database.

**Principle:** a database is a machine at an address. SQL is its package.

| Step | Folder | Adds | Lesson |
|---|---|---|---|
| 01 | `01-api` | FastAPI + Groq on Vercel | The key lives on your server, not in the browser |
| 02 | `02-file` | Save plans to `memory.txt` | Breaks on Vercel: read-only file system |
| 03 | `03-db` | Save plans to Supabase | Survives refreshes and redeploys |
| 04 | `04-page` | One HTML page with one fetch | The browser only asks; no key in the network tab |

## Setup

```bash
pip install fastapi uvicorn requests "supabase>=2.33" httpie
npm i -g vercel && vercel login
cp .env.example .env          # fill in your keys
set -a; source .env; set +a
```

Each folder deploys as its own Vercel project. From inside a folder:

```bash
vercel link
while IFS== read -r k v; do printf %s "$v" | vercel env add "$k" production; done < ../.env
vercel --prod
```

## 01 · Deploy the API

```bash
cd 01-api
uvicorn api.index:app --reload
http POST :8000/api/diagnose workflow="I edit until Sunday"
```

Open `/docs`, then deploy and run the same POST against `https://<app>.vercel.app`.

| Dial | Value |
|---|---|
| Address | `<app>.vercel.app/api/diagnose` |
| Action | POST |
| Key | none today (L8) |
| Package | `{"workflow"}` in, `{"plan"}` out |

## 02 · Connect a file

```bash
cd 02-file
uvicorn api.index:app --reload
http POST :8000/api/diagnose workflow="one"
http :8000/api/plans
```

It works locally. Deploy it and POST again: **500, read-only file system**. A Vercel function has no disk you own.

Locally, have two people POST at the same moment. Both get 200, but only one plan is saved: each request read the old file, and the last write wins.

What a real store must do:
1. Survive the server being thrown away.
2. Take many writers without losing one.
3. Answer "every plan for workflow 1, oldest first" without reading everything.

## 03 · Connect a database

1. Create a Supabase project. Settings → API gives you one URL and a secret key.
2. Run `03-db/schema.sql` in the SQL editor.
3. Deploy `03-db`.

```bash
http POST https://<app>.vercel.app/api/diagnose workflow="I edit until Sunday"
http https://<app>.vercel.app/api/workflows/1/diagnoses
```

Redeploy, then GET again. The plan is still there.

| SQL | L6 model |
|---|---|
| `create table` | block → table |
| column | fact |
| `primary key` | key |
| `references` | pointer |
| `default now()` | the `memory.txt` timestamp |

`workflow_id = 1` is hardcoded on purpose; L8 fixes it. The secret key bypasses every lock, so it lives only in server env vars.

## 04 · Add the page

```bash
cp -r 04-page/public 03-db/
cd 03-db && vercel --prod
```

Open the URL, type a workflow, get a plan. The page and the API are on the same origin, so there's no CORS. Open Network: the only request goes to your URL, and it carries no key.

## Done equals

A classmate opens your URL, gets a plan, refreshes, and the plan is still there. They search the network tab and find no key.

## Flags

- Vercel: the file system is read-only except `/tmp`. The first call after idle is slower.
- Supabase: free projects pause after 7 idle days. `sb_secret_` keys need `supabase>=2.33`.
- Groq: 30 requests per minute on the free tier. Model: `openai/gpt-oss-120b`.
