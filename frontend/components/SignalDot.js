"use client";

const CONFIG = {
  high: { rings: 3, color: "#2DD4BF", pulse: true, label: "High signal" },
  medium: { rings: 2, color: "#E8A33D", pulse: true, label: "Medium signal" },
  low: { rings: 1, color: "#8B97AC", pulse: false, label: "Low signal" },
  none: { rings: 0, color: "#3A4762", pulse: false, label: "No signal" },
};

export default function SignalDot({ level = "none" }) {
  const cfg = CONFIG[level] || CONFIG.none;
  return (
    <span className="relative inline-flex items-center justify-center w-4 h-4" title={cfg.label}>
      {cfg.pulse && (
        <span className="absolute inline-flex h-full w-full rounded-full opacity-40 animate-ping"
              style={{ backgroundColor: cfg.color }} />
      )}
      <span className="relative inline-flex rounded-full w-2 h-2" style={{ backgroundColor: cfg.color }} />
      {Array.from({ length: cfg.rings - 1 }).map((_, i) => (
        <span key={i} className="absolute rounded-full border"
              style={{ borderColor: cfg.color, opacity: 0.25,
                       width: `${8 + (i + 1) * 6}px`, height: `${8 + (i + 1) * 6}px` }} />
      ))}
    </span>
  );
}
