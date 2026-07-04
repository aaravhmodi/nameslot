"use client";

import { useState } from "react";

const EVENTS = [
  { id: "GOAL", label: "Goal", intensity: "high" },
  { id: "LATE_GOAL", label: "Late Winner", intensity: "high" },
  { id: "THROUGH_BALL", label: "Through Ball", intensity: "medium" },
  { id: "SHOT_SAVED", label: "Shot Saved", intensity: "medium" },
  { id: "ASSIST", label: "Assist", intensity: "medium" },
  { id: "YELLOW_CARD", label: "Yellow Card", intensity: "low" },
  { id: "SUBSTITUTION", label: "Substitution", intensity: "low" },
  { id: "HAT_TRICK", label: "Hat Trick", intensity: "high" },
];

interface Props {
  playerId: string;
  displayName: string;
}

export default function EventPanel({ playerId, displayName }: Props) {
  const [lastLine, setLastLine] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [loading, setLoading] = useState(false);

  async function triggerEvent(eventId: string, intensity: string) {
    setLoading(true);
    const res = await fetch("http://localhost:8000/events/trigger", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: playerId, event_id: eventId, intensity }),
    });
    const data = await res.json();
    setLastLine(data.text_preview);
    setAudioUrl(`http://localhost:8000${data.audio_url}`);
    setLoading(false);
  }

  return (
    <div className="space-y-4 border rounded-xl p-6">
      <h2 className="text-xl font-semibold">Commentary events — {displayName}</h2>

      <div className="grid grid-cols-2 gap-3">
        {EVENTS.map((ev) => (
          <button
            key={ev.id}
            onClick={() => triggerEvent(ev.id, ev.intensity)}
            disabled={loading}
            className="border rounded px-4 py-2 hover:bg-gray-100 disabled:opacity-50 text-left"
          >
            {ev.label}
          </button>
        ))}
      </div>

      {lastLine && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-2">
          <p className="italic text-gray-700">"{lastLine}"</p>
          {audioUrl && <audio controls src={audioUrl} className="w-full" />}
        </div>
      )}
    </div>
  );
}
