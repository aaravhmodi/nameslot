"use client";

import { useState } from "react";

interface Props {
  onCreated: (player: { player_id: string; display_name: string }) => void;
}

export default function PlayerForm({ onCreated }: Props) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [hint, setHint] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const res = await fetch("http://localhost:8000/players/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        pronunciation_hint: hint || undefined,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      setError(data.detail || "Failed to create player.");
      setLoading(false);
      return;
    }

    onCreated(data);
    setLoading(false);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-lg border border-lime-300/25 bg-zinc-950/80 p-5 shadow-xl shadow-black/30 backdrop-blur"
    >
      <div>
        <p className="text-xs font-bold uppercase text-lime-200/80">Player setup</p>
        <h2 className="mt-1 text-xl font-black text-white">Create match voice</h2>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
        <input
          className="min-w-0 rounded border border-white/15 bg-black/45 px-3 py-3 text-white placeholder:text-zinc-500 outline-none transition focus:border-lime-300"
          placeholder="First name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <input
          className="min-w-0 rounded border border-white/15 bg-black/45 px-3 py-3 text-white placeholder:text-zinc-500 outline-none transition focus:border-lime-300"
          placeholder="Last name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
      </div>

      <input
        className="w-full rounded border border-white/15 bg-black/45 px-3 py-3 text-white placeholder:text-zinc-500 outline-none transition focus:border-cyan-300"
        placeholder="Pronunciation hint (optional, e.g. MO-dee)"
        value={hint}
        onChange={(e) => setHint(e.target.value)}
      />

      {error && <p className="rounded border border-red-400/30 bg-red-950/50 px-3 py-2 text-sm text-red-100">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded bg-lime-300 px-4 py-3 text-sm font-black uppercase text-black transition hover:bg-cyan-200 disabled:opacity-50"
      >
        {loading ? "Generating name audio..." : "Generate Name Audio"}
      </button>
    </form>
  );
}
