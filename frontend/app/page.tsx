"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { runOutreach, OutreachRequest } from '../lib/api';

const PIPELINE_STEPS = [
  { icon: "⚡", label: "Harvesting signals", desc: "SerpAPI + NewsAPI" },
  { icon: "🧠", label: "Generating brief", desc: "Llama 3.3 70B" },
  { icon: "📡", label: "Sending email", desc: "Gmail SMTP" },
];

export default function HomePage() {
  const router = useRouter();
  const [form, setForm] = useState<OutreachRequest>({
    icp: '',
    target_company: '',
    recipient_email: '',
    sender_name: 'Alex'
  });
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!form.icp || !form.target_company || !form.recipient_email || !form.sender_name) {
      setError("All fields are required");
      return;
    }
    setError("");
    setLoading(true);

    // Simulate step progression
    setCurrentStep(0);
    const stepTimer1 = setTimeout(() => setCurrentStep(1), 3000);
    const stepTimer2 = setTimeout(() => setCurrentStep(2), 6000);

    try {
      const result = await runOutreach(form);
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      localStorage.setItem("firereach_result", JSON.stringify(result));
      router.push("/result");
    } catch (err: any) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setError(err.message || "Agent failed. Check API keys.");
      setLoading(false);
      setCurrentStep(-1);
    }
  };

  return (
    <div className="min-h-screen grid-bg scanline relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-orange-500/5 blur-[100px] rounded-full pointer-events-none" />

      <div className="relative z-10 max-w-2xl mx-auto px-6 py-16">
        
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-2 h-2 rounded-full bg-orange-500 animate-pulse-orange" />
            <span className="font-mono text-xs text-orange-500/70 tracking-widest uppercase">
              Autonomous Outreach Engine v1.0
            </span>
          </div>
          <h1 className="text-5xl font-bold tracking-tight mb-3">
            Fire<span className="text-orange-500 glow-orange-text">Reach</span>
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed">
            Drop your ICP. We find the signal, write the email, hit send.
            <span className="text-orange-500/70"> Zero templates. Zero humans.</span>
          </p>
        </div>

        {/* Pipeline Preview */}
        <div className="flex items-center gap-2 mb-10 p-4 border border-slate-800 rounded-lg bg-slate-900/40">
          {PIPELINE_STEPS.map((step, i) => (
            <div key={i} className="flex items-center gap-2 flex-1">
              <div className={`flex flex-col items-center gap-1 flex-1 p-2 rounded-md transition-all duration-500 ${
                currentStep === i
                  ? "bg-orange-500/10 border border-orange-500/30"
                  : currentStep > i
                  ? "opacity-40"
                  : "opacity-30"
              }`}>
                <span className="text-lg">{step.icon}</span>
                <span className="font-mono text-[10px] text-slate-300 text-center leading-tight">{step.label}</span>
                <span className="font-mono text-[9px] text-slate-500 text-center">{step.desc}</span>
              </div>
              {i < 2 && (
                <div className={`text-slate-600 text-xs transition-colors ${currentStep > i ? "text-orange-500" : ""}`}>
                  →
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Form */}
        <div className="space-y-4">
          
          {/* ICP */}
          <div className="space-y-1.5">
            <label className="font-mono text-xs text-slate-400 tracking-wider uppercase flex items-center gap-2">
              <span className="text-orange-500">01</span> Ideal Customer Profile
            </label>
            <textarea
              rows={3}
              placeholder="We sell high-end cybersecurity training to Series B startups."
              value={form.icp}
              onChange={e => setForm(p => ({ ...p, icp: e.target.value }))}
              disabled={loading}
              className="w-full bg-slate-900/60 border border-slate-700/60 rounded-lg px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-orange-500/50 focus:bg-slate-900 resize-none transition-all disabled:opacity-40"
            />
          </div>

          {/* Target Company */}
          <div className="space-y-1.5">
            <label className="font-mono text-xs text-slate-400 tracking-wider uppercase flex items-center gap-2">
              <span className="text-orange-500">02</span> Target Company
            </label>
            <input
              type="text"
              placeholder="Deel"
              value={form.target_company}
              onChange={e => setForm(p => ({ ...p, target_company: e.target.value }))}
              disabled={loading}
              className="w-full bg-slate-900/60 border border-slate-700/60 rounded-lg px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-orange-500/50 focus:bg-slate-900 transition-all disabled:opacity-40"
            />
          </div>

          {/* Two columns */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="font-mono text-xs text-slate-400 tracking-wider uppercase flex items-center gap-2">
                <span className="text-orange-500">03</span> Send To
              </label>
              <input
                type="email"
                placeholder="prospect@company.com"
                value={form.recipient_email}
                onChange={e => setForm(p => ({ ...p, recipient_email: e.target.value }))}
                disabled={loading}
                className="w-full bg-slate-900/60 border border-slate-700/60 rounded-lg px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-orange-500/50 focus:bg-slate-900 transition-all disabled:opacity-40"
              />
            </div>
            <div className="space-y-1.5">
              <label className="font-mono text-xs text-slate-400 tracking-wider uppercase flex items-center gap-2">
                <span className="text-orange-500">04</span> Your Name
              </label>
              <input
                type="text"
                placeholder="Alex"
                value={form.sender_name}
                onChange={e => setForm(p => ({ ...p, sender_name: e.target.value }))}
                disabled={loading}
                className="w-full bg-slate-900/60 border border-slate-700/60 rounded-lg px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-orange-500/50 focus:bg-slate-900 transition-all disabled:opacity-40"
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg font-mono text-xs text-red-400">
              ⚠ {error}
            </div>
          )}

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full mt-2 py-4 px-6 bg-orange-500 hover:bg-orange-400 disabled:opacity-50 disabled:cursor-not-allowed text-black font-bold text-sm tracking-wide rounded-lg transition-all duration-200 glow-orange flex items-center justify-center gap-3 group"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                <span className="font-mono">
                  {currentStep >= 0 ? PIPELINE_STEPS[currentStep]?.label + "..." : "Initializing..."}
                </span>
              </>
            ) : (
              <>
                <span>Launch Agent</span>
                <span className="group-hover:translate-x-1 transition-transform">→</span>
              </>
            )}
          </button>
        </div>

        {/* Footer */}
        <div className="mt-10 pt-6 border-t border-slate-800/50 flex items-center justify-between">
          <span className="font-mono text-[10px] text-slate-600">
            Signal → Research → Send
          </span>
          <span className="font-mono text-[10px] text-slate-600">
            Groq · SerpAPI · Gmail SMTP
          </span>
        </div>
      </div>
    </div>
  );
}
