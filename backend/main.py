import csv
import io
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import joinedload
from manual_founders import MANUAL_FOUNDERS
from db import Event, get_session, init_db

app = FastAPI(title="SG Tech Events + Founder Tracker")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"],
                    allow_methods=["*"], allow_headers=["*"])

SIGNAL_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3}


@app.on_event("startup")
def startup():
    init_db()


def serialize_event(event):
    return {
        "id": event.id, "name": event.name, "source": event.source,
        "source_url": event.source_url, "date_text": event.date_text,
        "venue": event.venue, "organizer": event.organizer, "category": event.category,
        "speakers": [{"name": sp.name, "title": sp.title, "company": sp.company,
                      "bio_snippet": sp.bio_snippet, "linkedin_url": sp.linkedin_url,
                      "company_url": sp.company_url, "is_founder": sp.is_founder,
                      "india_signal": sp.india_signal,
                      "india_signal_reason": sp.india_signal_reason}
                     for sp in event.speakers],
    }


def get_flagged_founders(min_signal="low"):
    session = get_session()
    events = session.query(Event).options(joinedload(Event.speakers)).all()
    results = []
    for event in events:
        for sp in event.speakers:
            if sp.is_founder != "yes":
                continue
            if SIGNAL_RANK.get(sp.india_signal, 0) < SIGNAL_RANK.get(min_signal, 1):
                continue
            results.append({
                "name": sp.name, "title": sp.title, "company": sp.company,
                "linkedin_url": sp.linkedin_url, "company_url": sp.company_url,
                "india_signal": sp.india_signal, "india_signal_reason": sp.india_signal_reason,
                "event_name": event.name, "event_date": event.date_text,
                "event_venue": event.venue, "event_url": event.source_url,
            })
    session.close()

    for m in MANUAL_FOUNDERS:
        results.append({
            "name": m["name"], "title": m["title"], "company": m["company"],
            "linkedin_url": None, "company_url": None,
            "india_signal": m["india_signal"], "india_signal_reason": m["india_signal_reason"] + " (manually researched)",
            "event_name": m["event_name"], "event_date": m["event_date"],
            "event_venue": None, "event_url": m["event_url"],
        })
    return results


@app.get("/events")
def list_events(category: str | None = None):
    session = get_session()
    query = session.query(Event).options(joinedload(Event.speakers))
    if category:
        query = query.filter(Event.category.ilike(f"%{category}%"))
    events = query.all()
    result = [serialize_event(e) for e in events]
    session.close()
    return result


@app.get("/founders")
def list_founders(min_signal: str = Query("low", enum=["low", "medium", "high"])):
    return get_flagged_founders(min_signal)


@app.get("/founders/export")
def export_founders_csv(min_signal: str = Query("low", enum=["low", "medium", "high"])):
    founders = get_flagged_founders(min_signal)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=[
        "name", "title", "company", "linkedin_url", "company_url",
        "india_signal", "india_signal_reason", "event_name", "event_date",
        "event_venue", "event_url",
    ])
    writer.writeheader()
    writer.writerows(founders)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=indian_founders.csv"},
    )