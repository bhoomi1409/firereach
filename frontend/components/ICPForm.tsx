"use client";

import { useState } from 'react';
import { runOutreach, OutreachRequest } from '../lib/api';

interface ICPFormProps {
  onSuccess: (result: any) => void;
  onError: (error: string) => void;
}

export default function ICPForm({ onSuccess, onError }: ICPFormProps) {
  const [formData, setFormData] = useState<OutreachRequest>({
    icp: '',
    target_company: '',
    recipient_email: '',
    sender_name: 'Alex'
  });
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setCurrentStep('🔍 Harvesting signals...');
    
    try {
      // Simulate step progression
      setTimeout(() => setCurrentStep('🧠 Generating brief...'), 2000);
      setTimeout(() => setCurrentStep('📧 Sending email...'), 4000);
      
      const result = await runOutreach(formData);
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
        <p className="text-slate-400 text-lg">Autonomous Outreach Engine</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-slate-800 p-8 rounded-lg">
        <div>
          <label className="block text-sm font-medium mb-2">
            ICP (Ideal Customer Profile)
          </label>
          <textarea
            value={formData.icp}
            onChange={(e) => setFormData({ ...formData, icp: e.target.value })}
            placeholder="We sell high-end cybersecurity training to Series B startups"
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Target Company
          </label>
          <input
            type="text"
            value={formData.target_company}
            onChange={(e) => setFormData({ ...formData, target_company: e.target.value })}
            placeholder="Stripe"
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Recipient Email
          </label>
          <input
            type="email"
            value={formData.recipient_email}
            onChange={(e) => setFormData({ ...formData, recipient_email: e.target.value })}
            placeholder="cto@targetcompany.com"
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Your Name
          </label>
          <input
            type="text"
            value={formData.sender_name}
            onChange={(e) => setFormData({ ...formData, sender_name: e.target.value })}
            placeholder="Alex"
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        {loading && (
          <div className="text-center py-4">
            <div className="inline-flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span className="text-blue-400">{currentStep}</span>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-md transition-colors"
        >
          {loading ? 'Agent Running...' : 'Launch Agent 🚀'}
        </button>
      </form>
    </div>
  );
}