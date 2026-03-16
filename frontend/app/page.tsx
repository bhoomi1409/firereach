"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface DiscoverRequest {
  icp_text: string;
  target_count: number;
}

interface ParsedICP {
  what_we_do: string;
  target_industry: string;
  target_stage: string;
  pain_keyword: string;
  solution_keyword: string;
  buyer_titles: string[];
  min_headcount: number;
  max_headcount: number;
  threshold: number;
}

interface DiscoveredCompany {
  name: string;
  domain: string;
  reason: string;
  approved: boolean;
}

interface DiscoverResponse {
  session_id: string;
  icp_parsed: ParsedICP;
  companies: DiscoveredCompany[];
}

const PIPELINE_STEPS = [
  { icon: "🔍", label: "Parsing ICP", desc: "Groq LLM Analysis" },
  { icon: "🏢", label: "Finding companies", desc: "Serper Discovery" },
  { icon: "📋", label: "Building list", desc: "Company Profiles" },
];

export default function HomePage() {
  const router = useRouter();
  const [icpText, setIcpText] = useState('We build AI voice agents for Series B fintech companies. They struggle with scaling customer support and need to reduce call times by 60%.');
  const [targetCount, setTargetCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [error, setError] = useState('');

  const handleDiscover = async () => {
    if (!icpText.trim() || icpText.trim().length < 20) {
      setError("Please describe your service and ideal customer in at least 20 characters");
      return;
    }
    
    // Prevent double-click race condition
    if (loading) return;
    
    setError("");
    setLoading(true);

    // Simulate step progression
    setCurrentStep(0);
    const stepTimer1 = setTimeout(() => setCurrentStep(1), 2000);
    const stepTimer2 = setTimeout(() => setCurrentStep(2), 4000);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/discover`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          icp_text: icpText,
          target_count: targetCount
        } as DiscoverRequest),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Discovery failed');
      }

      const result: DiscoverResponse = await response.json();
      
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      
      localStorage.setItem("firereach_session", JSON.stringify(result));
      router.push("/companies");
    } catch (err: any) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setError(err.message || "Discovery failed. Check your ICP description.");
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
              FireReach v4.0 — Fully Autonomous
            </span>
          </div>
          <h1 className="text-5xl font-bold tracking-tight mb-3">
            Fire<span className="text-orange-500 glow-orange-text">Reach</span>
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed">
            One ICP text → discover → approve → 7 signals → email + brochure → send
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
        <div className="space-y-6">
          
          {/* ICP Text Input */}
          <div className="space-y-2">
            <label className="font-mono text-xs text-slate-400 tracking-wider uppercase flex items-center gap-2">
              <span className="text-orange-500">01</span> Describe your service and ideal customer
            </label>
            <textarea
              rows={4}
              placeholder="We build AI voice agents for Series B fintech companies. They struggle with scaling customer support and need to reduce call times by 60%."
              value={icpText}
              onChange={e => setIcpText(e.target.value)}
              disabled={loading}
              className="w-full bg-slate-900/60 border border-slate-700/60 rounded-lg px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-orange-500/50 focus:bg-slate-900 resize-none transition-all disabled:opacity-40"
            />
            <div className="text-xs text-slate-500 font-mono">
              {icpText.length}/200+ characters • Be specific about industry, company stage, and pain points
            </div>
          </div>

          {/* Target Count Slider */}
          <div className="space-y-2">
            <label className="font-mono text-xs text-slate-400 tracking-wider uppercase flex items-center gap-2">
              <span className="text-orange-500">02</span> Target {targetCount} companies
            </label>
            <div className="flex items-center gap-4">
              <span className="text-xs text-slate-500 font-mono">1</span>
              <input
                type="range"
                min="1"
                max="20"
                value={targetCount}
                onChange={e => setTargetCount(parseInt(e.target.value))}
                disabled={loading}
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <span className="text-xs text-slate-500 font-mono">20</span>
            </div>
            <div className="text-xs text-slate-500 font-mono">
              System will discover {targetCount} companies matching your ICP for approval
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
            onClick={handleDiscover}
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
                <span>🔍 Find Companies</span>
                <span className="group-hover:translate-x-1 transition-transform">→</span>
              </>
            )}
          </button>
        </div>

        {/* Footer */}
        <div className="mt-10 pt-6 border-t border-slate-800/50 flex items-center justify-between">
          <span className="font-mono text-[10px] text-slate-600">
            Parse → Discover → Approve → Execute
          </span>
          <span className="font-mono text-[10px] text-slate-600">
            Groq · Serper · Hunter · Gmail SMTP
          </span>
        </div>
      </div>
    </div>
  );
}
