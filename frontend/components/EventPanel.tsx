"use client";

import { useEffect, useRef, useState } from "react";

const API_BASE = "http://localhost:8000";

const EVENTS = [
  { id: "GOAL", label: "Goal", intensity: "high", key: "1" },
  { id: "LATE_GOAL", label: "Late Winner", intensity: "high", key: "2" },
  { id: "THROUGH_BALL", label: "Through Ball", intensity: "medium", key: "3" },
  { id: "SHOT_SAVED", label: "Shot Saved", intensity: "medium", key: "4" },
  { id: "ASSIST", label: "Assist", intensity: "medium", key: "5" },
  { id: "YELLOW_CARD", label: "Yellow Card", intensity: "low", key: "6" },
  { id: "SUBSTITUTION", label: "Substitution", intensity: "low", key: "7" },
  { id: "HAT_TRICK", label: "Hat Trick", intensity: "high", key: "8" },
];

interface ClipHistoryItem {
  eventLabel: string;
  line: string;
  audioUrl: string;
  createdAt: string;
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

  return (
    <section className="space-y-5 border rounded-lg p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">Live commentary - {displayName}</h2>
          <p className="text-sm text-gray-500">Use keys 1-8 while FIFA is running.</p>
        </div>

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={autoPlay}
            onChange={(event) => setAutoPlay(event.target.checked)}
          />
          Auto-play
        </label>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {EVENTS.map((ev) => (
          <button
            key={ev.id}
            onClick={() => triggerEvent(ev.id, ev.intensity, ev.label)}
            disabled={Boolean(loadingEvent)}
            className="min-h-20 border rounded-md px-3 py-2 text-left hover:bg-gray-100 disabled:opacity-50"
          >
            <span className="block text-xs text-gray-500">Key {ev.key}</span>
            <span className="block font-medium">{ev.label}</span>
            {loadingEvent === ev.id && (
              <span className="mt-1 block text-xs text-gray-500">Generating...</span>
            )}
          </button>
        ))}
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {lastLine && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-2">
          <p className="italic text-gray-700">"{lastLine}"</p>
          {audioUrl && <audio ref={audioRef} controls src={audioUrl} className="w-full" />}
        </div>
      )}

      {history.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold uppercase text-gray-500">Recent clips</h3>
          <div className="divide-y rounded-md border">
            {history.map((item) => (
              <button
                key={`${item.createdAt}-${item.audioUrl}`}
                type="button"
                onClick={() => setAudioUrl(item.audioUrl)}
                className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left hover:bg-gray-50"
              >
                <span>
                  <span className="block text-sm font-medium">{item.eventLabel}</span>
                  <span className="block text-sm text-gray-500">{item.line}</span>
                </span>
                <span className="shrink-0 text-xs text-gray-400">{item.createdAt}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
