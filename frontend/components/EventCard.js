import SignalDot from "./SignalDot";

export default function EventCard({ event }) {
  const flaggedSpeakers = event.speakers.filter((s) => s.is_founder === "yes");
  return (
    <div className="border border-border bg-panel rounded-md p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-4">
        <h3 className="font-display text-xl leading-snug text-ink">{event.name}</h3>
        <span className="font-mono text-xs text-muted whitespace-nowrap pt-1">{event.date_text || "date tbc"}</span>
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted font-mono">
        {event.venue && <span>{event.venue}</span>}
        {event.category && <span className="text-amber uppercase tracking-wide text-xs self-center">{event.category}</span>}
        <a href={event.source_url} target="_blank" rel="noreferrer"
           className="ml-auto underline decoration-border hover:decoration-amber text-muted hover:text-amber">
          source: {event.source}
        </a>
      </div>
      {flaggedSpeakers.length > 0 && (
        <div className="mt-2 border-t border-border pt-3 flex flex-col gap-2">
          <span className="text-xs uppercase tracking-wide text-muted font-mono">Founders flagged ({flaggedSpeakers.length})</span>
          {flaggedSpeakers.map((sp, i) => (
            <div key={i} className="flex items-start gap-3 text-sm">
              <div className="pt-1"><SignalDot level={sp.india_signal} /></div>
              <div>
                <span className="text-ink font-medium">{sp.name}</span>
                {sp.company && <span className="text-muted"> — {sp.company}</span>}
                {sp.india_signal_reason && <p className="text-xs text-muted mt-0.5">{sp.india_signal_reason}</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
