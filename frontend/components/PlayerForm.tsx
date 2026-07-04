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

    if (!res.ok) {
      setError("Failed to create player.");
      setLoading(false);
      return;
    }

    const data = await res.json();
    onCreated(data);
    setLoading(false);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 border rounded-xl p-6">
      <h2 className="text-xl font-semibold">Create your player</h2>

      <div className="flex gap-3">
        <input
          className="border rounded px-3 py-2 flex-1"
          placeholder="First name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <input
          className="border rounded px-3 py-2 flex-1"
          placeholder="Last name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
      </div>

      <input
        className="border rounded px-3 py-2 w-full"
        placeholder="Pronunciation hint (optional, e.g. MO-dee)"
        value={hint}
        onChange={(e) => setHint(e.target.value)}
      />

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800 disabled:opacity-50"
      >
        {loading ? "Generating name audio…" : "Generate Name Audio"}
      </button>
    </form>
  );
}
