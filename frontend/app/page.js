"use client";

import { useEffect, useMemo, useState } from "react";
import EventCard from "../components/EventCard";
import SignalDot from "../components/SignalDot";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

function parseEventDate(dateText) {
  if (!dateText) return null;
  const cleaned = dateText
    .replace(/[•·]/g, " ")
    .replace(/(\d+)(st|nd|rd|th)/gi, "$1")
    .trim();

  const months = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec";
  const yearMatch = cleaned.match(/\b(20\d{2})\b/);
  const year = yearMatch ? yearMatch[1] : "2026";

  // Try "Day Month" first — this matches your actual data, e.g. "20 August", "7-8 October"
  let m = cleaned.match(new RegExp("\\b(\\d{1,2})(?:\\s*-\\s*\\d{1,2})?\\s+(" + months + ")[a-z]*", "i"));
  if (m) {
    const guess = new Date(m[2] + " " + m[1] + " " + year);
    if (!isNaN(guess.getTime())) return guess;
  }

  // Fallback: "Month Day" e.g. "August 27" — but don't match a time like "August 4 PM"
  m = cleaned.match(new RegExp("\\b(" + months + ")[a-z]*\\.?\\s+(\\d{1,2})\\b(?!\\s*(AM|PM|:))", "i"));
  if (m) {
    const guess = new Date(m[1] + " " + m[2] + " " + year);
    if (!isNaN(guess.getTime())) return guess;
  }

  const fallback = new Date(cleaned);
  return isNaN(fallback.getTime()) ? null : fallback;
}

export default function Dashboard() {
  const [events, setEvents] = useState([]);
  const [founders, setFounders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState("events");

  useEffect(function () {
    fetch(API_BASE + "/events")
      .then(function (r) { return r.json(); })
      .then(function (data) { setEvents(data); })
      .catch(function (e) { setError(String(e)); });

    fetch(API_BASE + "/founders?min_signal=low")
      .then(function (r) { return r.json(); })
      .then(function (data) { setFounders(data); })
      .catch(function (e) { setError(String(e)); })
      .finally(function () { setLoading(false); });
  }, []);

  const counts = useMemo(function () {
    const c = { high: 0, medium: 0, low: 0 };
    founders.forEach(function (f) {
      if (c[f.india_signal] !== undefined) c[f.india_signal] = c[f.india_signal] + 1;
    });
    return c;
  }, [founders]);

  const sortedEvents = useMemo(function () {
    const withDates = events.map(function (e) {
      return { event: e, parsed: parseEventDate(e.date_text) };
    });
    withDates.sort(function (a, b) {
      if (a.parsed && b.parsed) return a.parsed - b.parsed;
      if (a.parsed && !b.parsed) return -1;
      if (!a.parsed && b.parsed) return 1;
      return 0;
    });
    return withDates.map(function (w) { return w.event; });
  }, [events]);

  const csvUrl = API_BASE + "/founders/export?min_signal=low";

  return (
    <main className="min-h-screen bg-base px-6 py-10 md:px-16">
      <div className="max-w-5xl mx-auto mb-8">
        <span className="font-mono text-xs uppercase tracking-widest text-amber">
          Aug - Oct 2026 - Singapore
        </span>
        <h1 className="font-display text-4xl md:text-5xl text-ink mt-2">
          Tech events and founder signal
        </h1>
        <p className="text-muted max-w-2xl mt-2">
          Scraped tech events plus flagged founder appearances with an India-connection signal.
        </p>
      </div>

      <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-3 mb-8 font-mono text-sm">
        <div className="border border-border bg-panel rounded-md px-4 py-3">
          <div className="text-2xl text-ink">{events.length}</div>
          <div className="text-muted text-xs uppercase tracking-wide">events found</div>
        </div>
        <div className="border border-border bg-panel rounded-md px-4 py-3">
          <div className="text-2xl text-ink">{founders.length}</div>
          <div className="text-muted text-xs uppercase tracking-wide">founders flagged</div>
        </div>
        <div className="border border-border bg-panel rounded-md px-4 py-3">
          <div className="text-2xl text-teal flex items-center gap-2">
            <SignalDot level="high" />
            {counts.high}
          </div>
          <div className="text-muted text-xs uppercase tracking-wide">high signal</div>
        </div>
        <div className="border border-border bg-panel rounded-md px-4 py-3">
          <div className="text-2xl text-amber flex items-center gap-2">
            <SignalDot level="medium" />
            {counts.medium}
          </div>
          <div className="text-muted text-xs uppercase tracking-wide">medium signal</div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto flex gap-2 mb-6 font-mono text-sm">
        <button
          onClick={function () { setTab("events"); }}
          className={tab === "events" ? "px-4 py-2 rounded-t-md border-b-2 border-amber text-ink" : "px-4 py-2 rounded-t-md border-b-2 border-transparent text-muted"}
        >
          All events ({events.length})
        </button>
        <button
          onClick={function () { setTab("founders"); }}
          className={tab === "founders" ? "px-4 py-2 rounded-t-md border-b-2 border-amber text-ink" : "px-4 py-2 rounded-t-md border-b-2 border-transparent text-muted"}
        >
          Indian founders ({founders.length})
        </button>
      </div>

      <div className="max-w-5xl mx-auto flex flex-col gap-4">
        {loading && <p className="text-muted font-mono text-sm">loading...</p>}
        {error && <p className="text-amber font-mono text-sm">error: {error}</p>}

        {!loading && tab === "events" && sortedEvents.map(function (event) {
          return <EventCard key={event.id} event={event} />;
        })}

        {!loading && tab === "founders" && founders.length > 0 && (
          <div>
            <a href={csvUrl} className="text-xs font-mono text-amber underline mb-2 inline-block">
              Download as CSV
            </a>
            <div className="border border-border bg-panel rounded-md divide-y divide-border">
              {founders.map(function (f, i) {
                return (
                  <div key={i} className="flex items-start gap-3 p-4 text-sm">
                    <div className="pt-1">
                      <SignalDot level={f.india_signal} />
                    </div>
                    <div className="flex-1">
                      <div className="text-ink font-medium">
                        {f.name}{f.title ? " - " + f.title : ""}
                      </div>
                      {f.company && <div className="text-muted text-xs">{f.company}</div>}
                      <div className="text-xs text-muted mt-1">{f.india_signal_reason}</div>
                      <div className="text-xs text-amber mt-1">
                        seen at: {f.event_name}{f.event_date ? " (" + f.event_date + ")" : ""}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}