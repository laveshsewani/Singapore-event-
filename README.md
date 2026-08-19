# SG Tech Events + Founder Signal — Aug–Oct 2026

Scrapes Singapore tech events from **four sources** (10times, Eventbrite,
conferenceindex.org, Peatix), keeps only events dated **Aug 1 – Oct 31, 2026**,
extracts them with a free Groq-hosted LLM, flags founder appearances with an
India-signal confidence level, and shows it all in a dashboard.

```
sg-tech-events/
├── backend/     FastAPI + Playwright + Groq extraction pipeline
└── frontend/    Next.js dashboard
```

## Step 1 — Get your free Groq API key
1. Go to console.groq.com and sign up (no card needed)
2. **API Keys → Create API Key** → copy it

## Step 2 — Open in VS Code
`File → Open Folder…` → select this `sg-tech-events` folder. Open two terminals
(`` Ctrl+` ``, then split).

## Step 3 — Backend setup (terminal 1)
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
playwright install chromium

cp .env.example .env
```
Open `.env` and paste in your Groq key.

## Step 4 — Run the scraper
```bash
python run_scrape.py
```
This will, for each of the 4 sources:
1. Launch headless Chromium, load the listing page, collect event links
2. Visit each event page and grab its text
3. Send the text to Groq (Llama 3.3 70B) to extract structured event + speaker data
4. **Drop anything outside Aug 1 – Oct 31, 2026** (you'll see `skip (outside Aug-Oct window)` lines in the terminal for those)
5. Send kept events' speakers to Groq again to flag founders + India-signal confidence
6. Save to `events.db` (SQLite, created automatically)
7. Skip near-duplicate events across sources (fuzzy name matching)

This takes a few minutes — it's deliberately paced with delays so it doesn't hammer the source sites.

**If a source's selectors are stale** (sites redesign over time), that source
will just log fewer/zero results — it won't crash the run. Check `backend/scraper/sources.py` and adjust the `link_selector` for that source if you get 0 results from it.

## Step 5 — Start the API
```bash
uvicorn main:app --reload --port 8000
```
Check `http://localhost:8000/events` shows JSON.

## Step 6 — Frontend setup (terminal 2)
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Open `http://localhost:3000` — the dashboard populates from whatever the scraper found, each flagged founder shown with a signal-strength dot.

## Step 7 — Iterate
- Re-run `python run_scrape.py` any time — duplicates are skipped automatically
- To reset all data: stop the backend, delete `backend/events.db`, re-run the scraper
- To change the date window again: edit `DATE_WINDOW_START` / `DATE_WINDOW_END` in `backend/scraper/sources.py`
- To add another source site: add an entry to the `SOURCES` list in the same file
