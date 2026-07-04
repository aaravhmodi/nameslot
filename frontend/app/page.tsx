"use client";

import { useState } from "react";
import PlayerForm from "@/components/PlayerForm";
import EventPanel from "@/components/EventPanel";

export default function Home() {
  const [player, setPlayer] = useState<{ player_id: string; display_name: string } | null>(null);

  return (
    <main className="max-w-2xl mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold">NameSlot</h1>
      <p className="text-gray-500">AI-generated commentary names for custom sports players.</p>

      <PlayerForm onCreated={setPlayer} />

      {player && (
        <EventPanel playerId={player.player_id} displayName={player.display_name} />
      )}
    </main>
  );
}
