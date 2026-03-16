"use client";

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

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

interface SessionData {
  session_id: string;
  icp_parsed: ParsedICP;
  companies: DiscoveredCompany[];
}

export default function CompaniesPage() {
  const router = useRouter();
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [companies, setCompanies] = useState<DiscoveredCompany[]>([]);
  const [newCompany, setNewCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [updateTimeout, setUpdateTimeout] = useState<NodeJS.Timeout | null>(null);
  const [progress, setProgress] = useState<{step: string, progress: number, message: string} | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("firereach_session");
    if (!stored) { 
      router.push("/"); 
      return; 
    }
    const data = JSON.parse(stored) as SessionData;
    setSessionData(data);
    setCompanies(data.companies);
  }, [router]);

  // Debounced update function
  const debouncedUpdate = useCallback(async (updatedCompanies: DiscoveredCompany[]) => {
    if (!sessionData) return;
    
    try {
      const approvedNames = updatedCompanies.filter(c => c.approved).map(c => c.name);
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/session/${sessionData.session_id}/companies`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved_names: approvedNames })
      });
    } catch (err) {
      console.error('Failed to update session:', err);
    }
  }, [sessionData]);

  const toggleCompany = async (index: number) => {
    const updated = [...companies];
    updated[index].approved = !updated[index].approved;
    setCompanies(updated);

    // Debounce backend updates to prevent race conditions
    if (updateTimeout) {
      clearTimeout(updateTimeout);
    }
    
    const timeout = setTimeout(() => {
      debouncedUpdate(updated);
    }, 300); // 300ms debounce
    
    setUpdateTimeout(timeout);
  };

  const addCompany = () => {
    if (!newCompany.trim()) return;
    const company: DiscoveredCompany = {
      name: newCompany.trim(),
      domain: `${newCompany.toLowerCase().replace(/\s+/g, '')}.com`,
      reason: "manually added",
      approved: true
    };
    setCompanies([...companies, company]);
    setNewCompany('');
  };

  const runOutreach = async () => {
    if (!sessionData) return;
    
    // Prevent double-click race condition
    if (loading) return;
    
    const approvedCount = companies.filter(c => c.approved).length;
    if (approvedCount === 0) {
      setError("Please select at least one company");
      return;
    }

    setError("");
    setLoading(true);
    setProgress({ step: 'starting', progress: 0, message: 'Initializing outreach pipeline...' });

    try {
      // Start SSE connection for real-time progress
      const eventSource = new EventSource(`${process.env.NEXT_PUBLIC_API_URL}/api/run/stream/${sessionData.session_id}`);
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.error) {
            setError(data.error);
            eventSource.close();
            return;
          }
          setProgress(data);
          
          if (data.step === 'completed') {
            eventSource.close();
          }
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setProgress(null);
      };

      // Start the actual outreach process
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionData.session_id,
          max_send: Math.min(approvedCount, 10)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Outreach failed');
      }

      const result = await response.json();
      localStorage.setItem("firereach_result", JSON.stringify(result));
      
      // Close SSE and navigate
      eventSource.close();
      setProgress(null);
      router.push("/result");
    } catch (err: any) {
      setError(err.message || "Outreach failed");
      setLoading(false);
      setProgress(null);
    }
  };

  if (!sessionData) {
    return (
      <div className="min-h-screen grid-bg flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-orange-500/30 border-t-orange-500 rounded-full animate-spin" />
      </div>
    );
  }

  const approvedCount = companies.filter(c => c.approved).length;
  const hasDemo = companies.some(c => c.is_demo);

  return (
    <div className="min-h-screen grid-bg scanline">
      <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-orange-500/3 blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-12">
        
        {/* Demo Mode Banner */}
        {hasDemo && (
          <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <div className="flex items-center gap-3">
              <span className="text-yellow-500">⚠️</span>
              <div>
                <div className="text-yellow-400 font-medium text-sm">Demo Mode Active</div>
                <div className="text-yellow-300/80 text-xs">
                  Add Serper API key for real company discovery. Current results are demo companies for testing.
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
              <span className="font-mono text-xs text-orange-500/70 tracking-widest uppercase">
                Companies Discovered
              </span>
            </div>
            <h1 className="text-3xl font-bold">
              Fire<span className="text-orange-500">Reach</span>
              <span className="text-slate-500 font-normal text-xl ml-3">/ Company Selection</span>
            </h1>
          </div>
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 border border-slate-700 text-slate-400 hover:border-orange-500/50 hover:text-orange-500 font-mono text-xs rounded-lg transition-all"
          >
            ← Start Over
          </button>
        </div>

        {/* ICP Summary */}
        <div className="mb-8 p-6 bg-slate-950/80 border border-slate-800 rounded-xl">
          <h2 className="font-mono text-xs text-slate-500 tracking-widest uppercase mb-4 flex items-center gap-2">
            <span className="text-orange-500">{"//"}
</span> Parsed ICP
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-slate-500">Service:</span>
              <p className="text-slate-300 mt-1">{sessionData.icp_parsed.what_we_do}</p>
            </div>
            <div>
              <span className="text-slate-500">Industry:</span>
              <span className="ml-2 text-orange-400">{sessionData.icp_parsed.target_industry}</span>
              <span className="ml-2 text-slate-400">•</span>
              <span className="ml-2 text-blue-400">{sessionData.icp_parsed.target_stage}</span>
            </div>
            <div>
              <span className="text-slate-500">Pain:</span>
              <p className="text-slate-300 mt-1">{sessionData.icp_parsed.pain_keyword}</p>
            </div>
            <div>
              <span className="text-slate-500">Buyers:</span>
              <p className="text-slate-300 mt-1">{sessionData.icp_parsed.buyer_titles.join(", ")}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Company List */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-mono text-xs text-slate-500 tracking-widest uppercase flex items-center gap-2">
                <span className="text-orange-500">{"//"}
</span> Companies ({companies.length})
              </h2>
              <span className="text-xs text-slate-400">
                {approvedCount} selected
              </span>
            </div>
            
            <div className="space-y-3 mb-6">
              {companies.map((company, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-lg border transition-all cursor-pointer ${
                    company.approved
                      ? 'bg-orange-500/10 border-orange-500/50 text-orange-100'
                      : 'bg-slate-900/60 border-slate-800/60 text-slate-300 hover:border-slate-700'
                  }`}
                  onClick={() => toggleCompany(i)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                        company.approved 
                          ? 'bg-orange-500 border-orange-500' 
                          : 'border-slate-600'
                      }`}>
                        {company.approved && (
                          <svg className="w-2.5 h-2.5 text-black" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <div>
                        <div className="font-medium">{company.name}</div>
                        <div className="text-xs text-slate-500">{company.domain}</div>
                      </div>
                    </div>
                    <div className="text-xs text-slate-500">
                      {company.reason}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Add Company */}
            <div className="p-4 border border-slate-800 rounded-lg bg-slate-900/40">
              <h3 className="font-mono text-xs text-slate-500 tracking-widest uppercase mb-3">
                Add Company Manually
              </h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Company name"
                  value={newCompany}
                  onChange={e => setNewCompany(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && addCompany()}
                  className="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-orange-500/50"
                />
                <button
                  onClick={addCompany}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm rounded transition-colors"
                >
                  Add
                </button>
              </div>
            </div>
          </div>

          {/* Action Panel */}
          <div className="lg:col-span-1">
            <div className="sticky top-6">
              <div className="p-6 bg-slate-950/80 border border-slate-800 rounded-xl">
                <h3 className="font-mono text-xs text-slate-500 tracking-widest uppercase mb-4 flex items-center gap-2">
                  <span className="text-orange-500">{"//"}
</span> Ready to Launch
                </h3>
                
                <div className="space-y-4 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Companies selected:</span>
                    <span className="text-orange-400 font-mono">{approvedCount}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">ICP threshold:</span>
                    <span className="text-blue-400 font-mono">{sessionData.icp_parsed.threshold}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Pipeline:</span>
                    <span className="text-green-400 font-mono">7 signals</span>
                  </div>
                </div>

                {error && (
                  <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg font-mono text-xs text-red-400">
                    ⚠ {error}
                  </div>
                )}

                {/* Real-time Progress */}
                {progress && (
                  <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-3 h-3 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
                      <span className="text-blue-400 font-mono text-xs">{progress.message}</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${progress.progress}%` }}
                      />
                    </div>
                    <div className="text-xs text-slate-500 mt-1 font-mono">{progress.progress}% complete</div>
                  </div>
                )}

                <button
                  onClick={runOutreach}
                  disabled={loading || approvedCount === 0}
                  className="w-full py-3 px-4 bg-orange-500 hover:bg-orange-400 disabled:opacity-50 disabled:cursor-not-allowed text-black font-bold text-sm rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                      <span>Running Outreach...</span>
                    </>
                  ) : (
                    <>
                      <span>🚀 Run Outreach on {approvedCount}</span>
                    </>
                  )}
                </button>

                <div className="mt-4 text-xs text-slate-500 space-y-1">
                  <div>• Enrich & score each company</div>
                  <div>• Harvest 7 types of signals</div>
                  <div>• Find decision-maker contacts</div>
                  <div>• Generate email + HTML brochure</div>
                  <div>• Send via Gmail SMTP</div>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}