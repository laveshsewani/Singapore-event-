import re
import asyncio
from rapidfuzz import fuzz
from sqlalchemy.exc import IntegrityError

from db import Event, Speaker, get_session, init_db
from scraper.extract import extract_event
from scraper.fetch import run_source
from scraper.founder_flag import flag_founders
from scraper.sources import SOURCES
from scraper.date_filter import is_in_window

GENERIC_LISTING_PATTERN = re.compile(r"(\d{4}\s*[/,]\s*\d{4}\s*[/,]\s*\d{4})")


def is_generic_listing(name):
    return bool(GENERIC_LISTING_PATTERN.search(name))


def is_duplicate(session, name, source_url):
    if session.query(Event).filter(Event.source_url == source_url).first():
        return True
    existing_names = [row[0] for row in session.query(Event.name).all()]
    return any(fuzz.token_sort_ratio(name.lower(), e.lower()) > 88 for e in existing_names)


async def run_pipeline():
    init_db()
    session = get_session()
    stats = {"links_found": 0, "extracted": 0, "skip_not_event": 0,
              "skip_generic": 0, "skip_date": 0, "skip_duplicate": 0, "saved": 0}

    for source in SOURCES:
        print(f"\n=== Scraping source: {source['name']} ===")
        try:
            pages = await run_source(source)
        except Exception as e:
            print(f"[{source['name']}] source failed entirely: {e}")
            continue
        stats["links_found"] += len(pages)

        for page in pages:
            data = extract_event(page["text"])
            if not data:
                stats["skip_not_event"] += 1
                continue
            stats["extracted"] += 1

            if is_generic_listing(data["name"]):
                print(f"  skip (generic multi-year listing): {data['name']}")
                stats["skip_generic"] += 1
                continue

            if not is_in_window(data.get("date_text")):
                print(f"  skip (outside Aug-Oct window): {data['name']} ({data.get('date_text')})")
                stats["skip_date"] += 1
                continue

            if is_duplicate(session, data["name"], page["url"]):
                print(f"  skip (duplicate): {data['name']}")
                stats["skip_duplicate"] += 1
                continue

            enriched_speakers = flag_founders(data.get("speakers", []))
            event = Event(
                source=page["source"], source_url=page["url"], name=data["name"],
                date_text=data.get("date_text"), venue=data.get("venue"),
                organizer=data.get("organizer"), category=data.get("category"),
            )
            for sp in enriched_speakers:
                event.speakers.append(Speaker(
                    name=sp["name"], title=sp.get("title"), company=sp.get("company"),
                    bio_snippet=sp.get("bio_snippet"),
                    linkedin_url=sp.get("linkedin_url"), company_url=sp.get("company_url"),
                    is_founder=sp.get("is_founder"),
                    india_signal=sp.get("india_signal"),
                    india_signal_reason=sp.get("india_signal_reason"),
                ))
            try:
                session.add(event)
                session.commit()
                print(f"  saved: {data['name']} ({len(enriched_speakers)} speakers)")
                stats["saved"] += 1
            except IntegrityError:
                session.rollback()
                print(f"  skip (duplicate URL at save time): {data['name']}")
                stats["skip_duplicate"] += 1

    session.close()
    print("\n=== SUMMARY ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(run_pipeline())