"use client";

import { useState } from "react";
import PlayerForm from "@/components/PlayerForm";
import EventPanel from "@/components/EventPanel";

export default function Home() {
  const [player, setPlayer] = useState<{ player_id: string; display_name: string } | null>(null);

  return (
    <main className="mx-auto max-w-6xl p-4 sm:p-6 lg:p-8 space-y-6">
      <header className="overflow-hidden rounded-lg border border-lime-300/25 bg-black/55 shadow-2xl shadow-lime-950/40 backdrop-blur">
        <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-5 p-6 sm:p-8">
            <div className="flex flex-wrap items-center gap-3">
              <span className="rounded bg-lime-300 px-2 py-1 text-xs font-black uppercase tracking-wide text-black">
                Live Desk
              </span>
              <span className="rounded border border-cyan-300/40 px-2 py-1 text-xs font-semibold uppercase text-cyan-200">
                Local overlay
              </span>
            </div>
            <div>
              <p className="text-sm font-semibold uppercase text-lime-200/80">NameSlot FC</p>
              <h1 className="mt-2 text-4xl font-black leading-tight text-white sm:text-5xl">
                Commentary Control Room
              </h1>
            </div>
            <p className="max-w-2xl text-base leading-7 text-zinc-300">
              Generate player-specific match calls, fire them from a hotkey soundboard,
              and export clean packs for the next EA FC modding pass.
            </p>
          </div>

          <div className="relative min-h-64 border-t border-lime-300/20 bg-emerald-950 lg:border-l lg:border-t-0">
            <div className="absolute inset-5 rounded border-2 border-white/45">
              <div className="absolute left-1/2 top-0 h-full w-px bg-white/45" />
              <div className="absolute left-1/2 top-1/2 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white/45" />
              <div className="absolute left-0 top-1/2 h-28 w-16 -translate-y-1/2 border-y-2 border-r-2 border-white/45" />
              <div className="absolute right-0 top-1/2 h-28 w-16 -translate-y-1/2 border-y-2 border-l-2 border-white/45" />
            </div>
            <div className="absolute bottom-6 left-6 rounded bg-black/70 px-3 py-2">
              <p className="text-xs uppercase text-zinc-400">Active player</p>
              <p className="text-lg font-black text-lime-200">{player?.display_name || "Awaiting player"}</p>
            </div>
            <div className="absolute right-6 top-6 rounded bg-lime-300 px-3 py-2 text-black">
              <p className="text-xs font-bold uppercase">Keys</p>
              <p className="text-2xl font-black">1-8</p>
            </div>
          </div>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <div className="space-y-4">
          <PlayerForm onCreated={setPlayer} />
          <section className="rounded-lg border border-cyan-300/20 bg-zinc-950/75 p-5 text-sm text-zinc-300 shadow-xl shadow-black/20">
            <h2 className="mb-2 text-base font-bold text-cyan-100">Signal chain</h2>
            <p className="leading-6">
              Route browser audio into your recording or game capture stack with a virtual
              audio device, then keep this panel open beside the match.
            </p>
          </section>
        </div>

        {player ? (
          <EventPanel playerId={player.player_id} displayName={player.display_name} />
        ) : (
          <section className="flex min-h-80 items-center justify-center rounded-lg border border-dashed border-lime-300/30 bg-black/45 p-8 text-center text-zinc-300">
            <div>
              <p className="text-sm font-bold uppercase text-lime-200">Bench empty</p>
              <p className="mt-2 text-lg font-semibold text-white">Create a player to unlock the live commentary hotkeys.</p>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
