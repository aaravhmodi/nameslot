"use client";

import { useEffect, useRef, useState } from "react";

const API_BASE = "http://localhost:8000";

const EVENTS = [
  { id: "GOAL", label: "Goal", intensity: "high", key: "1", tone: "lime" },
  { id: "LATE_GOAL", label: "Late Winner", intensity: "high", key: "2", tone: "lime" },
  { id: "THROUGH_BALL", label: "Through Ball", intensity: "medium", key: "3", tone: "cyan" },
  { id: "SHOT_SAVED", label: "Shot Saved", intensity: "medium", key: "4", tone: "cyan" },
  { id: "ASSIST", label: "Assist", intensity: "medium", key: "5", tone: "cyan" },
  { id: "YELLOW_CARD", label: "Yellow Card", intensity: "low", key: "6", tone: "amber" },
  { id: "SUBSTITUTION", label: "Substitution", intensity: "low", key: "7", tone: "amber" },
  { id: "HAT_TRICK", label: "Hat Trick", intensity: "high", key: "8", tone: "lime" },
];

interface ClipHistoryItem {
  eventLabel: string;
  line: string;
  audioUrl: string;
  createdAt: string;
}

interface ExportPack {
  pack_name: string;
  pack_path: string;
  zip_file: string;
  clips_exported: number;
}

interface Props {
  playerId: string;
  displayName: string;
}

export default function EventPanel({ playerId, displayName }: Props) {
  const [lastLine, setLastLine] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [loadingEvent, setLoadingEvent] = useState("");
  const [error, setError] = useState("");
  const [autoPlay, setAutoPlay] = useState(true);
  const [history, setHistory] = useState<ClipHistoryItem[]>([]);
  const [exportPack, setExportPack] = useState<ExportPack | null>(null);
  const [exporting, setExporting] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (!audioUrl || !autoPlay) {
      return;
    }

    audioRef.current?.play().catch(() => {
      setError("Browser blocked autoplay. Press play once, then hotkeys will work.");
    });
  }, [audioUrl, autoPlay]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      const selected = EVENTS.find((item) => item.key === event.key);
      if (selected) {
        event.preventDefault();
        triggerEvent(selected.id, selected.intensity, selected.label);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  });

  async function triggerEvent(eventId: string, intensity: string, eventLabel: string) {
    if (loadingEvent) {
      return;
    }

    setLoadingEvent(eventId);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/events/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_id: playerId, event_id: eventId, intensity }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Failed to trigger event.");
        return;
      }

      const nextAudioUrl = `${API_BASE}${data.audio_url}`;
      setLastLine(data.text_preview);
      setAudioUrl(nextAudioUrl);
      setHistory((items) => [
        {
          eventLabel,
          line: data.text_preview,
          audioUrl: nextAudioUrl,
          createdAt: new Date().toLocaleTimeString(),
        },
        ...items,
      ].slice(0, 6));
    } catch {
      setError("Could not reach the commentary API on localhost:8000.");
    } finally {
      setLoadingEvent("");
    }
  }

  async function exportForEafc() {
    setExporting(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/exports/eafc/${playerId}`, {
        method: "POST",
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Failed to export EA FC pack.");
        return;
      }
      setExportPack(data);
    } catch {
      setError("Could not reach the export API on localhost:8000.");
    } finally {
      setExporting(false);
    }
  }

  return (
    <section className="space-y-5 rounded-lg border border-lime-300/25 bg-black/65 p-5 shadow-2xl shadow-black/30 backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase text-cyan-200/80">Match audio board</p>
          <h2 className="mt-1 text-2xl font-black text-white">Live commentary - {displayName}</h2>
          <p className="text-sm text-zinc-400">Use keys 1-8 while the match is running.</p>
        </div>

        <label className="flex items-center gap-2 rounded border border-white/10 bg-white/5 px-3 py-2 text-sm text-zinc-200">
          <input
            type="checkbox"
            checked={autoPlay}
            onChange={(event) => setAutoPlay(event.target.checked)}
            className="accent-lime-300"
          />
          Auto-play
        </label>
      </div>

      <div className="flex flex-wrap items-center gap-3 rounded-md border border-cyan-300/20 bg-cyan-950/25 p-3">
        <button
          type="button"
          onClick={exportForEafc}
          disabled={exporting}
          className="rounded bg-cyan-300 px-4 py-2 text-sm font-black uppercase text-black transition hover:bg-lime-300 disabled:opacity-50"
        >
          {exporting ? "Exporting..." : "Export EA FC pack"}
        </button>

        {exportPack && (
          <div className="text-sm text-zinc-300">
            <span className="font-black text-lime-200">{exportPack.clips_exported}</span> clips exported
            to <span className="font-mono text-white">{exportPack.pack_name}</span>
            {" "}
            <a
              className="font-bold text-cyan-200 underline"
              href={`${API_BASE}/exports/download/${exportPack.zip_file}`}
            >
              Download zip
            </a>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {EVENTS.map((ev) => (
          <button
            key={ev.id}
            onClick={() => triggerEvent(ev.id, ev.intensity, ev.label)}
            disabled={Boolean(loadingEvent)}
            className={[
              "min-h-24 rounded-md border px-3 py-3 text-left transition disabled:opacity-50",
              "bg-zinc-950/80 hover:-translate-y-0.5 hover:bg-white/10",
              ev.tone === "lime" ? "border-lime-300/40 shadow-lime-950/40" : "",
              ev.tone === "cyan" ? "border-cyan-300/35 shadow-cyan-950/40" : "",
              ev.tone === "amber" ? "border-amber-300/35 shadow-amber-950/40" : "",
              loadingEvent === ev.id ? "ring-2 ring-lime-300" : "",
            ].join(" ")}
          >
            <span className="flex items-center justify-between gap-2">
              <span className="text-xs font-bold uppercase text-zinc-400">Key {ev.key}</span>
              <span className="rounded bg-white/10 px-2 py-0.5 text-xs font-bold uppercase text-zinc-300">
                {ev.intensity}
              </span>
            </span>
            <span className="mt-3 block text-lg font-black text-white">{ev.label}</span>
            {loadingEvent === ev.id && (
              <span className="mt-2 block text-xs font-bold uppercase text-lime-200">Generating...</span>
            )}
          </button>
        ))}
      </div>

      {error && <p className="rounded border border-red-400/30 bg-red-950/60 px-3 py-2 text-sm text-red-100">{error}</p>}

      {lastLine && (
        <div className="space-y-3 rounded-lg border border-lime-300/25 bg-lime-950/20 p-4">
          <div className="flex items-start gap-3">
            <span className="mt-1 h-3 w-3 shrink-0 rounded-full bg-lime-300 shadow-lg shadow-lime-300/40" />
            <p className="text-lg font-semibold italic text-lime-50">"{lastLine}"</p>
          </div>
          {audioUrl && <audio ref={audioRef} controls src={audioUrl} className="w-full" />}
        </div>
      )}

      {history.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-bold uppercase text-zinc-400">Recent clips</h3>
          <div className="divide-y divide-white/10 rounded-md border border-white/10">
            {history.map((item) => (
              <button
                key={`${item.createdAt}-${item.audioUrl}`}
                type="button"
                onClick={() => setAudioUrl(item.audioUrl)}
                className="flex w-full items-center justify-between gap-3 px-3 py-3 text-left transition hover:bg-white/10"
              >
                <span>
                  <span className="block text-sm font-bold text-white">{item.eventLabel}</span>
                  <span className="block text-sm text-zinc-400">{item.line}</span>
                </span>
                <span className="shrink-0 text-xs text-zinc-500">{item.createdAt}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
