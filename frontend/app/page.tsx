"use client";

import { useState } from "react";
import PlayerForm from "@/components/PlayerForm";
import EventPanel from "@/components/EventPanel";

export default function Home() {
  const [player, setPlayer] = useState<{ player_id: string; display_name: string } | null>(null);

  return (
    <main className="mx-auto max-w-5xl p-6 space-y-6">
      <header className="space-y-2">
        <p className="text-sm font-semibold uppercase text-gray-500">FIFA overlay scaffold</p>
        <h1 className="text-3xl font-bold">NameSlot Commentary Desk</h1>
        <p className="max-w-2xl text-gray-500">
          Generate player-specific commentary clips, then trigger them from a hotkey soundboard
          while the game is running.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <div className="space-y-4">
          <PlayerForm onCreated={setPlayer} />
          <section className="rounded-lg border p-5 text-sm text-gray-600">
            <h2 className="mb-2 text-base font-semibold text-gray-900">Next integration step</h2>
            <p>
              Route browser audio into your recording or game capture stack with a virtual
              audio device, then keep this panel open beside FIFA.
            </p>
          </section>
        </div>

        {player ? (
          <EventPanel playerId={player.player_id} displayName={player.display_name} />
        ) : (
          <section className="flex min-h-80 items-center justify-center rounded-lg border border-dashed p-8 text-center text-gray-500">
            Create a player to unlock the live commentary hotkeys.
          </section>
        )}
      </div>
    </main>
  );
}
