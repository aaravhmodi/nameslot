"use client";

import { useState } from "react";

const API_BASE = "http://localhost:8000";

interface TimelineItem {
  time: number;
  frame_url: string;
  width: number;
  height: number;
  detected: boolean;
  star: null | {
    x: number;
    y: number;
    width: number;
    height: number;
    confidence: number;
  };
  player_anchor: null | {
    x: number;
    y: number;
  };
}

interface AnalysisResult {
  video_id: string;
  frames_sampled: number;
  detections: number;
  detection_rate: number;
  timeline: TimelineItem[];
}

export default function VideoUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyzeVideo(event: React.FormEvent) {
    event.preventDefault();
    if (!file) {
      setError("Choose a gameplay clip first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const body = new FormData();
    body.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/video/analyze-star`, {
        method: "POST",
        body,
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Video analysis failed.");
        return;
      }
      setResult(data);
    } catch {
      setError("Could not reach the video API on localhost:8000.");
    } finally {
      setLoading(false);
    }
  }

  const previewItems = result?.timeline.filter((item) => item.detected).slice(0, 8) || [];

  return (
    <div className="space-y-6">
      <form
        onSubmit={analyzeVideo}
        className="space-y-4 rounded-lg border border-white/10 bg-[#101613]/85 p-5 shadow-xl shadow-black/25 backdrop-blur"
      >
        <div>
          <p className="text-xs font-medium uppercase text-stone-400">Career mode marker</p>
          <h2 className="mt-1 text-2xl font-semibold text-stone-50">Yellow star detector</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-stone-300">
            Upload a gameplay clip and NameSlot will sample frames, find the yellow star above
            your player, and build a first-pass timeline for later commentary generation.
          </p>
        </div>

        <label className="block rounded-lg border border-dashed border-white/15 bg-white/[0.035] p-5">
          <span className="block text-sm font-medium text-stone-200">Gameplay video</span>
          <input
            type="file"
            accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            className="mt-3 block w-full text-sm text-stone-300 file:mr-4 file:rounded-md file:border-0 file:bg-[#d7c37a] file:px-4 file:py-2 file:text-sm file:font-semibold file:text-[#151512]"
          />
          {file && <span className="mt-2 block text-xs text-stone-500">{file.name}</span>}
        </label>

        {error && <p className="rounded-md border border-red-300/25 bg-red-950/35 px-3 py-2 text-sm text-red-100">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-[#d7c37a] px-4 py-3 text-sm font-semibold uppercase text-[#151512] transition hover:bg-stone-100 disabled:opacity-50"
        >
          {loading ? "Analyzing clip..." : "Analyze yellow star"}
        </button>
      </form>

      {result && (
        <section className="space-y-4 rounded-lg border border-white/10 bg-[#101613]/85 p-5 shadow-xl shadow-black/25 backdrop-blur">
          <div className="grid gap-3 sm:grid-cols-4">
            <Stat label="Video ID" value={result.video_id} />
            <Stat label="Frames" value={String(result.frames_sampled)} />
            <Stat label="Detections" value={String(result.detections)} />
            <Stat label="Rate" value={`${Math.round(result.detection_rate * 100)}%`} />
          </div>

          {previewItems.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {previewItems.map((item) => (
                <div key={`${item.time}-${item.frame_url}`} className="overflow-hidden rounded-lg border border-white/10 bg-black/20">
                  <div className="relative">
                    <img
                      src={`${API_BASE}${item.frame_url}`}
                      alt={`Detected star at ${item.time}s`}
                      className="aspect-video w-full object-cover"
                    />
                    {item.star && (
                      <div
                        className="absolute border-2 border-[#d7c37a]"
                        style={{
                          left: `${(item.star.x / item.width) * 100}%`,
                          top: `${(item.star.y / item.height) * 100}%`,
                          width: `${Math.max((item.star.width / item.width) * 100, 3)}%`,
                          height: `${Math.max((item.star.height / item.height) * 100, 3)}%`,
                          transform: "translate(-50%, -50%)",
                        }}
                      />
                    )}
                    {item.player_anchor && (
                      <div
                        className="absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#9ab6bd]"
                        style={{
                          left: `${(item.player_anchor.x / item.width) * 100}%`,
                          top: `${(item.player_anchor.y / item.height) * 100}%`,
                        }}
                      />
                    )}
                  </div>
                  <div className="flex items-center justify-between px-3 py-2 text-sm">
                    <span className="font-medium text-stone-50">{item.time.toFixed(2)}s</span>
                    <span className="text-stone-400">confidence {item.star?.confidence ?? 0}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="rounded-md border border-white/10 bg-white/[0.035] px-3 py-3 text-sm text-stone-300">
              No yellow star was detected in the sampled frames. Try a clip where the player marker is visible and not hidden by camera cuts or menus.
            </p>
          )}
        </section>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-white/10 bg-white/[0.04] p-3">
      <p className="text-xs font-medium uppercase text-stone-500">{label}</p>
      <p className="mt-1 break-all text-lg font-semibold text-stone-50">{value}</p>
    </div>
  );
}
