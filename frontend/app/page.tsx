"use client";

import { useState } from "react";
import Link from "next/link";
import PlayerForm from "@/components/PlayerForm";
import EventPanel from "@/components/EventPanel";

export default function Home() {
  const [player, setPlayer] = useState<{ player_id: string; display_name: string } | null>(null);

  return (
    <main className="mx-auto max-w-6xl p-4 sm:p-6 lg:p-8 space-y-6">
      <header className="overflow-hidden rounded-lg border border-white/10 bg-[#101613]/85 shadow-2xl shadow-black/25 backdrop-blur">
        <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-5 p-6 sm:p-8">
            <div className="flex flex-wrap items-center gap-3">
              <span className="rounded-sm bg-[#d7c37a] px-2 py-1 text-xs font-bold uppercase tracking-wide text-[#151512]">
                Live Desk
              </span>
              <span className="rounded-sm border border-white/15 px-2 py-1 text-xs font-medium uppercase text-stone-300">
                Local overlay
              </span>
            </div>
            <div>
              <p className="text-sm font-medium uppercase text-stone-400">NameSlot FC</p>
              <h1 className="mt-2 text-4xl font-semibold leading-tight text-stone-50 sm:text-5xl">
                Commentary Control Room
              </h1>
            </div>
            <p className="max-w-2xl text-base leading-7 text-stone-300">
              Generate player-specific match calls, fire them from a hotkey soundboard,
              and export clean packs for the next EA FC modding pass.
            </p>
            <Link
              href="/video"
              className="inline-flex rounded-md border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-medium text-stone-100 transition hover:bg-white/[0.08]"
            >
              Analyze gameplay video
            </Link>
          </div>

          <div className="relative min-h-64 border-t border-white/10 bg-[#173324] lg:border-l lg:border-t-0">
            <div className="absolute inset-6 rounded-sm border border-white/35">
              <div className="absolute left-1/2 top-0 h-full w-px bg-white/30" />
              <div className="absolute left-1/2 top-1/2 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/30" />
              <div className="absolute left-0 top-1/2 h-28 w-16 -translate-y-1/2 border-y border-r border-white/30" />
              <div className="absolute right-0 top-1/2 h-28 w-16 -translate-y-1/2 border-y border-l border-white/30" />
            </div>
            <div className="absolute bottom-6 left-6 rounded-sm bg-black/45 px-3 py-2 backdrop-blur">
              <p className="text-xs uppercase text-stone-400">Active player</p>
              <p className="text-lg font-semibold text-stone-50">{player?.display_name || "Awaiting player"}</p>
            </div>
            <div className="absolute right-6 top-6 rounded-sm bg-stone-100/90 px-3 py-2 text-[#151512]">
              <p className="text-xs font-semibold uppercase">Keys</p>
              <p className="text-2xl font-semibold">1-8</p>
            </div>
          </div>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <div className="space-y-4">
          <PlayerForm onCreated={setPlayer} />
          <section className="rounded-lg border border-white/10 bg-[#101613]/80 p-5 text-sm text-stone-300 shadow-xl shadow-black/20">
            <h2 className="mb-2 text-base font-semibold text-stone-50">Signal chain</h2>
            <p className="leading-6">
              Route browser audio into your recording or game capture stack with a virtual
              audio device, then keep this panel open beside the match.
            </p>
          </section>
        </div>

        {player ? (
          <EventPanel playerId={player.player_id} displayName={player.display_name} />
        ) : (
          <section className="flex min-h-80 items-center justify-center rounded-lg border border-dashed border-white/15 bg-[#101613]/70 p-8 text-center text-stone-300">
            <div>
              <p className="text-sm font-medium uppercase text-stone-400">Bench empty</p>
              <p className="mt-2 text-lg font-medium text-stone-50">Create a player to unlock the live commentary hotkeys.</p>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
