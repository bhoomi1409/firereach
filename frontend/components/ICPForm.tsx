"use client";

import { useState } from 'react';

interface ICPFormProps {
  onSuccess: (result: any) => void;
  onError: (error: string) => void;
}

interface AutonomousRequest {
  what_we_do: string;
  what_they_do: string;
  why_they_need_us: string;
  max_companies: number;
}

export default function ICPForm({ onSuccess, onError }: ICPFormProps) {
  const [formData, setFormData] = useState<AutonomousRequest>({
    what_we_do: 'We sell AI-powered outreach automation to B2B sales teams',
    what_they_do: 'Series B SaaS companies with a sales team trying to grow pipeline',
    why_they_need_us: 'Low reply rates, hired new VP Sales, raised funding to grow revenue',
    max_companies: 5
  });
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setCurrentStep('🔍 Discovering companies from ICP...');
    
    try {
      // Simulate step progression for autonomous pipeline
      setTimeout(() => setCurrentStep('📊 Enriching & scoring companies...'), 3000);
      setTimeout(() => setCurrentStep('🎯 Finding contacts & harvesting signals...'), 6000);
      setTimeout(() => setCurrentStep('📧 Generating & sending personalized emails...'), 9000);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/outreach`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Request failed');
      }

      const result = await response.json();
      onSuccess(result);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setLoading(false);
      setCurrentStep('');
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2">🔥 FireReach</h1>
        <p className="text-slate-400 text-lg">Fully Autonomous Outreach Engine</p>
        <p className="text-slate-500 text-sm mt-2">
          Describe your ICP → System finds companies → Scores → Contacts → Sends
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-slate-800 p-8 rounded-lg">
        <div>
          <label className="block text-sm font-medium mb-2 text-orange-400">
            What We Do
          </label>
          <textarea
            value={formData.what_we_do}
            onChange={(e) => setFormData({ ...formData, what_we_do: e.target.value })}
            placeholder="We sell AI-powered outreach automation to B2B sales teams"
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-transparent text-white"
            rows={2}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-orange-400">
            What They Do (Target Companies)
          </label>
          <textarea
            value={formData.what_they_do}
            onChange={(e) => setFormData({ ...formData, what_they_do: e.target.value })}
            placeholder="Series B SaaS companies with a sales team trying to grow pipeline"
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-transparent text-white"
            rows={2}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-orange-400">
            Why They Need Us (Pain Points)
          </label>
          <textarea
            value={formData.why_they_need_us}
            onChange={(e) => setFormData({ ...formData, why_they_need_us: e.target.value })}
            placeholder="Low reply rates, hired new VP Sales, raised funding to grow revenue"
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-transparent text-white"
            rows={2}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-orange-400">
            Max Companies to Contact
          </label>
          <select
            value={formData.max_companies}
            onChange={(e) => setFormData({ ...formData, max_companies: parseInt(e.target.value) })}
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-transparent text-white"
          >
            <option value={1}>1 company</option>
            <option value={3}>3 companies</option>
            <option value={5}>5 companies</option>
            <option value={10}>10 companies</option>
            <option value={15}>15 companies</option>
            <option value={20}>20 companies</option>
          </select>
        </div>

        {loading && (
          <div className="text-center py-4">
            <div className="inline-flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-500"></div>
              <span className="text-orange-400">{currentStep}</span>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium py-4 px-6 rounded-md transition-all duration-200"
        >
          {loading ? 'Autonomous Agent Running...' : '🚀 Start Autonomous Outreach'}
        </button>
      </form>
    </div>
  );
}