"""
All source sites the pipeline scrapes. Add/remove entries here — no other
code needs to change.
"""

SOURCES = [
    {
        "name": "10times",
        "listing_url": "https://10times.com/singapore/technology",
        "link_selector": "a.thumb-t, a.link_of_event",
    },
    {
        "name": "eventbrite",
        "listing_url": "https://www.eventbrite.sg/d/singapore--singapore/tech-conferences/",
        "link_selector": "a.event-card-link",
    },
    {
        "name": "conferenceindex",
        "listing_url": "https://conferenceindex.org/conferences/information-technology/singapore-sg",
        "link_selector": "a",
    },
    {
        "name": "peatix",
        "listing_url": "https://peatix.com/search?q=tech&country=SG",
        "link_selector": "a.event-card, a[href*='/event/']",
    },
]

# Date window for this run: August 1 - October 31, 2026
DATE_WINDOW_START = "2026-08-01"
DATE_WINDOW_END = "2026-10-31"
