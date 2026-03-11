"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { OutreachResponse } from '../../lib/api';

export default function ResultPage() {
  const router = useRouter();
  const [result, setResult] = useState<OutreachResponse | null>(null);
  const [visibleLog, setVisibleLog] = useState<string[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem("firereach_result");
    if (!stored) { router.push("/"); return; }
    const data = JSON.parse(stored) as OutreachResponse;
    setResult(data);

    // Animate log entries one by one
    data.execution_log.forEach((entry, i) => {
      setTimeout(() => {
        setVisibleLog(prev => [...prev, entry]);
      }, i * 400);
    });
  }, [router]);

  if (!result) return (
    <div className="min-h-screen grid-bg flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-orange-500/30 border-t-orange-500 rounded-full animate-spin" />
    </div>
  );

  const signals = result.signals;
  const signalItems = [
    { label: "Funding", value: signals.funding_rounds, icon: "💰" },
    { label: "Hiring", value: signals.hiring_trends?.join(" · "), icon: "👥" },
    { label: "Leadership", value: signals.leadership_changes, icon: "🎯" },
    { label: "Tech Stack", value: signals.tech_stack_changes, icon: "⚙️" },
    { label: "News", value: signals.news_mentions?.[0], icon: "📰" },
  ].filter(s => s.value);

  return (
    <div className="min-h-screen grid-bg scanline">
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-orange-500/3 blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 max-w-3xl mx-auto px-6 py-12">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="font-mono text-xs text-green-500/70 tracking-widest uppercase">
                Mission Complete
              </span>
            </div>
            <h1 className="text-3xl font-bold">
              Fire<span className="text-orange-500">Reach</span>
              <span className="text-slate-500 font-normal text-xl ml-3">/ Results</span>
            </h1>
          </div>
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 border border-slate-700 text-slate-400 hover:border-orange-500/50 hover:text-orange-500 font-mono text-xs rounded-lg transition-all"
          >
            ← Run Again
          </button>
        </div>

        {/* Agent Log */}
        <div className="mb-6 p-5 bg-slate-950/80 border border-slate-800 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
            <span className="font-mono text-xs text-slate-500 ml-2">agent.log</span>
          </div>
          <div className="space-y-1.5">
            {visibleLog.map((entry, i) => (
              <div key={i} className="font-mono text-xs text-slate-300 animate-slide-in flex gap-3">
                <span className="text-slate-600 select-none">{String(i + 1).padStart(2, "0")}</span>
                <span className={
                  entry.includes("✅") ? "text-green-400" :
                  entry.includes("⚠️") ? "text-yellow-400" :
                  entry.includes("❌") ? "text-red-400" :
                  entry.includes("🔍") || entry.includes("🧠") || entry.includes("📧") ? "text-orange-400" :
                  "text-slate-300"
                }>{entry}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Signals Grid */}
        <div className="mb-6">
          <h2 className="font-mono text-xs text-slate-500 tracking-widest uppercase mb-3 flex items-center gap-2">
            <span className="text-orange-500">//</span> Signals Harvested ({signalItems.length})
          </h2>
          <div className="grid gap-2">
            {signalItems.map((signal, i) => (
              <div key={i} className="flex gap-3 p-3 bg-slate-900/60 border border-slate-800/60 rounded-lg">
                <span className="text-base mt-0.5">{signal.icon}</span>
                <div className="flex-1 min-w-0">
                  <span className="font-mono text-[10px] text-orange-500/70 uppercase tracking-wider">{signal.label}</span>
                  <p className="text-xs text-slate-300 mt-0.5 leading-relaxed line-clamp-2">{signal.value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Account Brief */}
        <div className="mb-6 p-5 bg-slate-900/60 border border-slate-800/60 rounded-xl">
          <h2 className="font-mono text-xs text-slate-500 tracking-widest uppercase mb-3 flex items-center gap-2">
            <span className="text-orange-500">//</span> Account Brief
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">{result.account_brief}</p>
        </div>

        {/* Email Preview */}
        <div className="p-5 bg-slate-900/60 border border-slate-800/60 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-mono text-xs text-slate-500 tracking-widest uppercase flex items-center gap-2">
              <span className="text-orange-500">//</span> Email Sent
            </h2>
            <span className={`font-mono text-xs px-2 py-1 rounded-full ${
              result.send_status
                ? "bg-green-500/10 text-green-400 border border-green-500/20"
                : "bg-red-500/10 text-red-400 border border-red-500/20"
            }`}>
              {result.send_status ? "✓ Delivered" : "✗ Failed"}
            </span>
          </div>

          {/* Subject */}
          <div className="mb-4 pb-4 border-b border-slate-800">
            <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider">Subject</span>
            <p className="text-sm font-semibold text-slate-100 mt-1">{result.email_subject}</p>
          </div>

          {/* Body */}
          <div>
            <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider">Body</span>
            <p className="text-sm text-slate-300 mt-2 leading-relaxed whitespace-pre-wrap">{result.email_body}</p>
          </div>

          {/* Send status */}
          <div className="mt-4 pt-4 border-t border-slate-800">
            <span className="font-mono text-[10px] text-slate-500">{result.send_message}</span>
          </div>
        </div>

      </div>
    </div>
  );
}
