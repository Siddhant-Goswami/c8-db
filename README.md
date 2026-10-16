# Lecture 7: A Database Is a Machine at an Address

Aarav's plan survives a refresh and a redeploy. The page that serves it is nothing but HTML, CSS and one fetch.

**Principle:** a database is a machine at an address. SQL is its package.

**Done equals:** a classmate opens your `vercel.app` URL, gets a plan, refreshes, and the plan is still there. They search the network tab and find no key.

Every arrow in this lecture uses the same four dials:

| Dial | Groq | Your API | Supabase |
|---|---|---|---|
| Address | `api.groq.com/openai/v1/chat/completions` | `<app>.vercel.app/api/diagnose` | `<project>.supabase.co/rest/v1/diagnoses` |
| Action | POST | POST | POST adds a row, GET reads rows |
| Key | required | none today (L8 debt) | `apikey` + `Authorization: Bearer` (service key, server only) |
| Package | `{model, messages}` | `{"workflow"}` in, `{"plan"}` out | `{"workflow_id":1,"plan":"...","tone":"plain"}` |

## The steps

Each folder is one step. Each step adds one idea to the step before it. A folder that has an `api/` folder deploys to Vercel as its own project. Two steps have no folder because httpie is the whole demo: two writers at once, and the first raw call to Supabase.

| Step | Files | What it adds | Debt or failure |
|---|---|---|---|
| 01 | `01-leak/index.html` | The browser calls Groq directly | The key shows in the Network tab |
| 02 | `02-function/diagnose.py` | Just the function, run from the terminal | The process was never the UI |
| 03 | `03-fastapi/api/index.py` | The function behind a FastAPI route, on Vercel | The key moves to your server |
| 04 | `04-gradio-client/app.py` | Gradio becomes a client of the live URL, with no key | Runs on your laptop only |
| 05 | `05-memory-txt/api/index.py` | Plans and roll call saved to `memory.txt`, plus `GET /api/plans` | 500 on Vercel: read-only file system |
| 06 | `06-schema/schema.sql` | `create table` written from the L6 model | POST now returns 201 |
| 07 | `07-supabase-sdk/sdk.py` | The same calls through the `supabase` SDK | The cushion hides the URL and headers |
| 08 | `08-supabase-api/api/index.py` | The server inserts and selects rows, and roll call inserts too | Survives redeploys. L6 debt paid |
| 09 | `09-html-client/public/index.html` | Gradio replaced by one fetch | No key in the browser. L5 debt paid |

## Room moves

The room plays the parts the lecture is about: the attacker who finds the key, the many writers who lose data, and the verifier who checks someone else's work. Three games run through all 120 minutes.

**1. Predict the status.** Before every run, the room posts a guess in chat. A right guess is 1 point, tallied in a Discord thread. The 🎯 marks below show each one.

| Moment | Answer |
|---|---|
| 01: is the key visible? | Yes, in plain text |
| 03: first live call | 200, but slow (cold start) |
| 05: POST on Vercel | 500, read-only file system |
| Two writers | 200 + 200, one plan saved |
| Supabase before the table | 404, `relation does not exist` |
| Supabase after `schema.sql` | 201 |
| 09: keys in the network tab? | 0 |

**2. The debt card.** Every student starts with three debts and stamps each one when *their own* deploy passes. They post every stamp to Discord with a screenshot.

- 🔑 L5: no key in my network tab
- 🔄 L6: my plan survives a refresh
- 🚀 Part 2: my plan survives a `vercel --prod`

A partner's "verified" closes the card. This is Done Equals, split into pieces students can see.

**3. Roll call stampede.** The whole room POSTs their name to your live URL, once in Part 2 and once in Part 4:

```bash
http POST https://<your-app>.vercel.app/api/roll name=Priya
```

`/api/roll` skips Groq on purpose. Sixty students on `/api/diagnose` would hit Groq's 30-requests-a-minute limit and get 500s for the wrong reason.

## Setup

```bash
pip install fastapi uvicorn requests gradio supabase httpie
npm i -g vercel && vercel login
export GROQ_API_KEY=gsk_...
export SUPABASE_URL=https://<project>.supabase.co
export SUPABASE_SERVICE_KEY=...
```

## Part 1 · Pay the key debt (0 to 30)

**01: The leak.** Paste a key into `01-leak/index.html` and open the file in a browser. 🎯 Is the key visible? Open Inspect, then Network, and click Send. Read the `Authorization` header aloud. Whose machine is this? Whose key? Who else can read it?

🎮 **Key hunt:** deploy the leak page with a throwaway key and drop the URL in chat. The first student to post the key's last 4 characters wins. Revoke the key on screen right after.

**02: Strip it down to the function.** The UI was never the process.

```bash
python 02-function/diagnose.py
```

**03: Put the function on your server.** 🎮 **Dial cards:** the room fills in the four dials for your API in chat before you type any FastAPI code. You type what they agree on.

```bash
cd 03-fastapi
uvicorn api.index:app --reload
http POST :8000/api/diagnose workflow="I edit until Sunday"
open http://127.0.0.1:8000/docs

vercel link
vercel env add GROQ_API_KEY
vercel --prod
http POST https://<app>.vercel.app/api/diagnose workflow="I edit until Sunday"
```

🎯 What does the first live call return? Vercel finds `app` in `api/index.py` on its own, so there's no config file.

🎮 **Stamp time (10 min):** students split their own L5 app and post a `/docs` screenshot. Anyone whose network tab is clean stamps 🔑.

**04: Gradio becomes a client.** Set `URL` in `04-gradio-client/app.py` and run `python app.py` on your laptop. The file holds no key. The key lives on the machine that spends the money.

## Part 2 · The file dies (30 to 50)

**05: Write plans to a file.** Each request reads `memory.txt`, asks Groq for a plan, and writes the file back with the new plan added. The empty `memory.txt` ships in the repo.

```bash
cd 05-memory-txt
uvicorn api.index:app --reload
http POST :8000/api/diagnose workflow="one"
http POST :8000/api/diagnose workflow="two"
http :8000/api/plans
```

Locally it works. Now run `vercel --prod`. 🎯 What will a POST to the live URL return?

🎮 **Stampede 1:** drop the live URL in chat. Everyone runs the roll call. Every single student gets a 500, read-only file system. A Vercel function has no disk you own, and the machine is thrown away after each request.

**Two writers.** Keep the step 05 server running locally. Two volunteers, two terminals, one count of three:

```bash
http POST :8000/api/diagnose workflow="Aarav: I edit until Sunday"
http POST :8000/api/diagnose workflow="Meera: research eats my mornings"
http :8000/api/plans
```

🎯 How many plans did the file keep? Two 200s, one plan. Both requests read the same old file, and the one that writes last wins.

What broke:
1. The data has to survive the server being thrown away.
2. Many writers have to be able to save without losing anything.
3. We need to answer "every plan for workflow 1, oldest first" without reading everything.

The data is too fragile for your server, so it moves to a machine built for it, reached by API. Size moved the LLM off your server. Survival moves storage.

## Part 3 · Another machine (50 to 85)

**Call the machine before it has a shape.** Create a Supabase project and open Settings → API. You'll see one URL and two keys. 🎮 **Dial cards** again: the room fills in Supabase's four dials before any code. 🎯 What will this POST return?

```bash
http POST $SUPABASE_URL/rest/v1/diagnoses apikey:$SUPABASE_SERVICE_KEY \
  "Authorization:Bearer $SUPABASE_SERVICE_KEY" workflow_id:=1 plan="Batch your edits." tone=plain
```

It fails with `relation "diagnoses" does not exist`. The machine needs a shape.

**06: SQL is the package language.** 🎮 **Shape the table:** before you type, the room calls out the columns from the L6 model, and you type only what they call out. Then check against `06-schema/schema.sql` and run it in the SQL editor. Map each line back to the L6 model:

| SQL | L6 model |
|---|---|
| `create table` | block → table |
| each line | fact → column |
| `primary key` | the key |
| `references` | the pointer |
| `default now()` | the `memory.txt` timestamp |

🎯 What does the same POST return now? 201, and the row shows up in the Table Editor. The last line of the schema file is Aarav's L6 question, and it covers requirement 3.

There are two keys:
- **anon / publishable** is for machines you don't control, like a browser (L9).
- **service_role / secret** bypasses every lock. Keep it in server env vars only. Leave Row Level Security alone today; L8 covers it.

**07: The cushion.** `python 07-supabase-sdk/sdk.py` makes the same two calls. 🎮 **What does it hide?** Each student names one thing the SDK hides (the URL, the headers, `apikey`, the JSON). Repeats don't count.

## Part 4 · Strip the cushion, ship it all (85 to 120)

**08: The server remembers.** The file append becomes an insert, and the L6 question becomes a route.

```bash
cd 08-supabase-api
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_KEY
vercel --prod
```

`workflow_id: 1` is hardcoded on purpose. L8 opens on that lie. Gradio from step 04 still works without changes.

🎮 **Stampede 2:** the same roll call, now to the step 08 URL. Put the `roll` table in the Table Editor on the projector and watch it fill. Sixty writers, sixty rows, on a machine nobody in this room owns. This is requirement 2, done by the room.

**09: Rip off Gradio.** All Gradio was hiding is a text box, a button, and one POST. `09-html-client/public/index.html` does just that. Read the fetch against the dials: address, action, package, and no key. `fetch` is `requests.post` running in the browser. Drop the page next to the step 08 API and redeploy the same project:

```bash
cp -r 09-html-client/public 08-supabase-api/
cd 08-supabase-api
vercel --prod
```

The page and the API are in one project with the same origin, so CORS never comes up. 🎯 How many keys are in the network tab?

If someone asks for a version with no JavaScript, a form is already a POST:

```html
<form method="post" action="/api/diagnose"><textarea name="workflow"></textarea><button>Diagnose</button></form>
```

The server would then need `Form(...)` and `PlainTextResponse`. Changing the package shape changes the server.

**The HLD:** Aarav's browser runs plain HTML. Your Vercel function exists only while it answers. Groq thinks. Supabase remembers.

**Proof, in debt order:**
1. Type a workflow on the live page, then run `http https://<app>.vercel.app/api/workflows/1/diagnoses`. You get one row.
2. Refresh. There's still one row, so the L6 debt is paid.
3. Change a comment, run `vercel --prod`, and GET again. There's still one row, so Part 2 is fixed.
4. Open Network and send. The only request goes to your URL, with no Groq key and no Supabase key. The L5 debt is paid.
5. 🎮 **Swap and verify:** swap URLs with a partner. They get a plan, refresh, search for a key, and post "verified" with your URL. Nobody verifies their own. That post stamps 🔄 and 🚀 and closes the debt card.

**Hook for L8:** your partner just read Aarav's plans without a password. Whose row is this?

## Practice set

1. **Split:** a FastAPI route on Vercel, and Gradio running locally with one URL and no key.
2. **Type your model:** every table, with `references` on every `_id`.
3. **Two verbs:** one insert route, and one select route that uses `where` and `order by`.
4. **Strip Gradio:** `public/index.html` with one fetch, in the same Vercel project.
5. **Get verified:** a classmate posts "verified" with your URL.

Rules: use httpie before the SDK. Keep keys out of Git, HTML and screenshots. Ask an LLM to explain errors, not to write your `create table`.

## Flags

- **Vercel:** the file system is read-only except for `/tmp`, and a cold start takes about 1 s. If `/` hits the function instead of `public/index.html`, add a `vercel.json` rewrite.
- **Supabase:** free projects pause after 7 idle days. `supabase` is pinned in `requirements.txt`.
- **Groq:** the free tier allows 30 requests per minute. Check the model name (`llama-3.3-70b-versatile`) on the day.
