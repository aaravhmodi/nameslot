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
    <section className="space-y-5 rounded-lg border border-white/10 bg-[#101613]/85 p-5 shadow-2xl shadow-black/25 backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase text-stone-400">Match audio board</p>
          <h2 className="mt-1 text-2xl font-semibold text-stone-50">Live commentary - {displayName}</h2>
          <p className="text-sm text-stone-400">Use keys 1-8 while the match is running.</p>
        </div>

        <label className="flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-stone-300">
          <input
            type="checkbox"
            checked={autoPlay}
            onChange={(event) => setAutoPlay(event.target.checked)}
            className="accent-[#d7c37a]"
          />
          Auto-play
        </label>
      </div>

      <div className="flex flex-wrap items-center gap-3 rounded-md border border-white/10 bg-white/[0.04] p-3">
        <button
          type="button"
          onClick={exportForEafc}
          disabled={exporting}
          className="rounded-md bg-[#9ab6bd] px-4 py-2 text-sm font-semibold uppercase text-[#101613] transition hover:bg-stone-100 disabled:opacity-50"
        >
          {exporting ? "Exporting..." : "Export EA FC pack"}
        </button>

        {exportPack && (
          <div className="text-sm text-stone-300">
            <span className="font-semibold text-stone-50">{exportPack.clips_exported}</span> clips exported
            to <span className="font-mono text-stone-100">{exportPack.pack_name}</span>
            {" "}
            <a
              className="font-medium text-[#d7c37a] underline"
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
              "bg-white/[0.045] hover:-translate-y-px hover:bg-white/[0.075]",
              ev.tone === "lime" ? "border-[#d7c37a]/35" : "",
              ev.tone === "cyan" ? "border-[#9ab6bd]/35" : "",
              ev.tone === "amber" ? "border-[#d09a52]/35" : "",
              loadingEvent === ev.id ? "ring-1 ring-[#d7c37a]" : "",
            ].join(" ")}
          >
            <span className="flex items-center justify-between gap-2">
              <span className="text-xs font-medium uppercase text-stone-400">Key {ev.key}</span>
              <span className="rounded-sm bg-white/10 px-2 py-0.5 text-xs font-medium uppercase text-stone-300">
                {ev.intensity}
              </span>
            </span>
            <span className="mt-3 block text-lg font-semibold text-stone-50">{ev.label}</span>
            {loadingEvent === ev.id && (
              <span className="mt-2 block text-xs font-medium uppercase text-[#d7c37a]">Generating...</span>
            )}
          </button>
        ))}
      </div>

      {error && <p className="rounded-md border border-red-300/25 bg-red-950/35 px-3 py-2 text-sm text-red-100">{error}</p>}

      {lastLine && (
        <div className="space-y-3 rounded-lg border border-white/10 bg-white/[0.045] p-4">
          <div className="flex items-start gap-3">
            <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-[#d7c37a]" />
            <p className="text-lg font-medium italic text-stone-50">"{lastLine}"</p>
          </div>
          {audioUrl && <audio ref={audioRef} controls src={audioUrl} className="w-full" />}
        </div>
      )}

      {history.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium uppercase text-stone-400">Recent clips</h3>
          <div className="divide-y divide-white/10 rounded-md border border-white/10">
            {history.map((item) => (
              <button
                key={`${item.createdAt}-${item.audioUrl}`}
                type="button"
                onClick={() => setAudioUrl(item.audioUrl)}
                className="flex w-full items-center justify-between gap-3 px-3 py-3 text-left transition hover:bg-white/[0.06]"
              >
                <span>
                  <span className="block text-sm font-medium text-stone-50">{item.eventLabel}</span>
                  <span className="block text-sm text-stone-400">{item.line}</span>
                </span>
                <span className="shrink-0 text-xs text-stone-500">{item.createdAt}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
