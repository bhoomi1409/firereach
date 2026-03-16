"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Signal {
  signal_id: string;
  type: string;
  summary: string;
  detected_at: string;
  type_weight: number;
  freshness: number;
  icp_relevance: number;
  final_score: number;
}

interface ContactResult {
  email: string;
  first_name: string;
  last_name: string;
  title: string;
  email_status: string;
  source: string;
  confidence: number;
}

interface CompanyResult {
  company_name: string;
  domain: string;
  icp_score: number;
  should_send: boolean;
  skip_reason?: string;
  signals_used: Signal[];
  contact?: ContactResult;
  email_subject?: string;
  email_body?: string;
  brochure_html?: string;
  sent: boolean;
  send_message: string;
  log: string[];
}

interface SkippedCompany {
  company_name: string;
  skip_reason: string;
}

interface BatchResult {
  batch_id: string;
  session_id: string;
  icp_summary: string;
  companies_discovered: number;
  companies_approved: number;
  companies_scored: number;
  companies_passed_icp: number;
  emails_sent: number;
  results: CompanyResult[];
  skipped: SkippedCompany[];
}

export default function ResultPage() {
  const router = useRouter();
  const [result, setResult] = useState<BatchResult | null>(null);
  const [selectedCompany, setSelectedCompany] = useState(0);

  useEffect(() => {
    const stored = localStorage.getItem("firereach_result");
    if (!stored) { router.push("/"); return; }
    const data = JSON.parse(stored) as BatchResult;
    setResult(data);
  }, [router]);

  if (!result) return (
    <div className="min-h-screen grid-bg flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-orange-500/30 border-t-orange-500 rounded-full animate-spin" />
    </div>
  );

  const currentResult = result.results[selectedCompany];

  return (
    <div className="min-h-screen grid-bg scanline">
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-orange-500/3 blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto px-6 py-12">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="font-mono text-xs text-green-500/70 tracking-widest uppercase">
                Autonomous Mission Complete
              </span>
            </div>
            <h1 className="text-3xl font-bold">
              Fire<span className="text-orange-500">Reach</span>
              <span className="text-slate-500 font-normal text-xl ml-3">/ Batch Results</span>
            </h1>
          </div>
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 border border-slate-700 text-slate-400 hover:border-orange-500/50 hover:text-orange-500 font-mono text-xs rounded-lg transition-all"
          >
            ← Run Again
          </button>
        </div>

        {/* Batch Summary */}
        <div className="mb-8 p-6 bg-slate-950/80 border border-slate-800 rounded-xl">
          <h2 className="font-mono text-xs text-slate-500 tracking-widest uppercase mb-4 flex items-center gap-2">
            <span className="text-orange-500">{"//"}
</span> Batch Summary
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-400">{result.companies_discovered}</div>
              <div className="text-xs text-slate-500 font-mono">Discovered</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">{result.companies_passed_icp}</div>
              <div className="text-xs text-slate-500 font-mono">Passed ICP</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{result.emails_sent}</div>
              <div className="text-xs text-slate-500 font-mono">Emails Sent</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">{result.skipped.length}</div>
              <div className="text-xs text-slate-500 font-mono">Skipped</div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-800">
            <div className="text-xs text-slate-400">
              <span className="font-mono text-orange-500">ICP:</span> {result.icp_summary}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Company List */}
          <div className="lg:col-span-1">
            <h2 className="font-mono text-xs text-slate-500 tracking-widest uppercase mb-3 flex items-center gap-2">
              <span className="text-orange-500">{"//"}
</span> Companies ({result.results.length + result.skipped.length})
            </h2>
            
            {/* Contacted Companies */}
            <div className="space-y-2 mb-4">
              {result.results.map((company, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedCompany(i)}
                  className={`w-full text-left p-3 rounded-lg border transition-all ${
                    selectedCompany === i
                      ? 'bg-orange-500/10 border-orange-500/50 text-orange-400'
                      : 'bg-slate-900/60 border-slate-800/60 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="font-medium text-sm">{company.company_name}</div>
                    <div className={`w-2 h-2 rounded-full ${
                      company.sent ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    ICP Score: {company.icp_score}% • {company.sent ? 'Sent' : 'Failed'}
                  </div>
                </button>
              ))}
            </div>

            {/* Skipped Companies */}
            {result.skipped.length > 0 && (
              <div>
                <h3 className="font-mono text-xs text-slate-600 tracking-widest uppercase mb-2">Skipped</h3>
                <div className="space-y-1">
                  {result.skipped.slice(0, 5).map((company, i) => (
                    <div key={i} className="p-2 bg-slate-900/40 border border-slate-800/40 rounded text-xs">
                      <div className="text-slate-400 font-medium">{company.company_name}</div>
                      <div className="text-slate-600 text-[10px] mt-1">{company.skip_reason}</div>
                    </div>
                  ))}
                  {result.skipped.length > 5 && (
                    <div className="text-xs text-slate-600 text-center py-2">
                      +{result.skipped.length - 5} more skipped
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Company Details */}
          <div className="lg:col-span-2">
            {currentResult ? (
              <div className="space-y-6">
                
                {/* Company Header */}
                <div className="p-5 bg-slate-900/60 border border-slate-800/60 rounded-xl">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xl font-bold text-white">{currentResult.company_name}</h3>
                    <span className={`font-mono text-xs px-3 py-1 rounded-full ${
                      currentResult.sent
                        ? "bg-green-500/10 text-green-400 border border-green-500/20"
                        : "bg-red-500/10 text-red-400 border border-red-500/20"
                    }`}>
                      {currentResult.sent ? "✓ Email Sent" : "✗ Send Failed"}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-slate-500">ICP Score:</span>
                      <span className="ml-2 font-mono text-orange-400">{currentResult.icp_score}%</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Contact:</span>
                      <span className="ml-2 text-slate-300">{currentResult.contact?.first_name} {currentResult.contact?.last_name || 'N/A'}</span>
                    </div>
                  </div>
                  {currentResult.contact?.email && (
                    <div className="mt-2 text-sm">
                      <span className="text-slate-500">Email:</span>
                      <span className="ml-2 text-slate-300">{currentResult.contact.email}</span>
                    </div>
                  )}
                </div>

                {/* Signals */}
                {currentResult.signals_used.length > 0 && (
                  <div className="p-5 bg-slate-900/60 border border-slate-800/60 rounded-xl">
                    <h4 className="font-mono text-xs text-slate-500 tracking-widest uppercase mb-3 flex items-center gap-2">
                      <span className="text-orange-500">{"//"}
</span> Top Signals ({currentResult.signals_used.length})
                    </h4>
                    <div className="space-y-2">
                      {currentResult.signals_used.map((signal, i) => (
                        <div key={i} className="flex gap-3 p-3 bg-slate-950/60 border border-slate-800/40 rounded-lg">
                          <span className="text-orange-400 font-mono text-xs mt-0.5">#{i + 1}</span>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs font-mono text-slate-400">{signal.type}</span>
                              <span className="text-xs text-slate-500">•</span>
                              <span className="text-xs text-slate-500">Score: {signal.final_score.toFixed(1)}</span>
                            </div>
                            <p className="text-xs text-slate-300 leading-relaxed">{signal.summary}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Email & Brochure Preview */}
                {currentResult.email_subject && (
                  <div className="p-5 bg-slate-900/60 border border-slate-800/60 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-mono text-xs text-slate-500 tracking-widest uppercase flex items-center gap-2">
                        <span className="text-orange-500">{"//"}
</span> Generated Email & Brochure
                      </h4>
                      <div className="flex gap-2">
                        <span className={`font-mono text-xs px-2 py-1 rounded-full ${
                          currentResult.sent
                            ? "bg-green-500/10 text-green-400 border border-green-500/20"
                            : "bg-red-500/10 text-red-400 border border-red-500/20"
                        }`}>
                          {currentResult.sent ? "✓ Email Sent" : "✗ Send Failed"}
                        </span>
                        {currentResult.brochure_html && (
                          <span className="font-mono text-xs px-2 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                            📄 HTML Brochure
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Subject */}
                    <div className="mb-4 pb-4 border-b border-slate-800">
                      <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider">Subject</span>
                      <p className="text-sm font-semibold text-slate-100 mt-1">{currentResult.email_subject}</p>
                    </div>

                    {/* Body */}
                    <div className="mb-4">
                      <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider">Body</span>
                      <p className="text-sm text-slate-300 mt-2 leading-relaxed whitespace-pre-wrap">{currentResult.email_body}</p>
                    </div>

                    {/* Brochure Preview */}
                    {currentResult.brochure_html && (
                      <div className="mb-4">
                        <span className="font-mono text-[10px] text-slate-500 uppercase tracking-wider">HTML Brochure Preview</span>
                        <div className="mt-2 p-4 bg-slate-950/60 border border-slate-800/40 rounded-lg max-h-60 overflow-y-auto">
                          <div 
                            className="text-xs"
                            dangerouslySetInnerHTML={{ __html: currentResult.brochure_html }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Send Status */}
                    <div className="pt-4 border-t border-slate-800">
                      <span className="font-mono text-[10px] text-slate-500">{currentResult.send_message}</span>
                    </div>
                  </div>
                )}

                {/* Agent Log */}
                <div className="p-5 bg-slate-950/80 border border-slate-800 rounded-xl">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 rounded-full bg-red-500/80" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                    <div className="w-3 h-3 rounded-full bg-green-500/80" />
                    <span className="font-mono text-xs text-slate-500 ml-2">agent.log - {currentResult.company_name}</span>
                  </div>
                  <div className="space-y-1.5 max-h-60 overflow-y-auto">
                    {currentResult.log.map((entry, i) => (
                      <div key={i} className="font-mono text-xs text-slate-300 flex gap-3">
                        <span className="text-slate-600 select-none">{String(i + 1).padStart(2, "0")}</span>
                        <span className={
                          entry.includes("✅") || entry.includes("OK") ? "text-green-400" :
                          entry.includes("⚠️") || entry.includes("failed") ? "text-yellow-400" :
                          entry.includes("❌") || entry.includes("error") ? "text-red-400" :
                          entry.includes("[") ? "text-orange-400" :
                          "text-slate-300"
                        }>{entry}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            ) : (
              <div className="p-8 bg-slate-900/60 border border-slate-800/60 rounded-xl text-center">
                <div className="text-slate-500">Select a company to view details</div>
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
