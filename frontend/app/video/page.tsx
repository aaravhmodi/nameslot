import Link from "next/link";
import VideoUploader from "@/components/VideoUploader";

export default function VideoAnalysisPage() {
  return (
    <main className="mx-auto max-w-6xl p-4 sm:p-6 lg:p-8 space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4 rounded-lg border border-white/10 bg-[#101613]/85 p-6 shadow-2xl shadow-black/25 backdrop-blur">
        <div>
          <p className="text-sm font-medium uppercase text-stone-400">Video lab</p>
          <h1 className="mt-2 text-4xl font-semibold text-stone-50">Gameplay analysis</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-stone-300">
            First-pass local computer vision for detecting the yellow star above your Career Mode player.
          </p>
        </div>
        <Link className="rounded-md border border-white/10 px-4 py-2 text-sm font-medium text-stone-200 hover:bg-white/[0.06]" href="/">
          Back to desk
        </Link>
      </header>

      <VideoUploader />
    </main>
  );
}
