"use client";

import { SignalData } from '../lib/api';

interface SignalCardProps {
  signals: SignalData;
}

export default function SignalCard({ signals }: SignalCardProps) {
  const signalItems = [
    { label: 'Funding', value: signals.funding_rounds, icon: '💰' },
    { label: 'Leadership', value: signals.leadership_changes, icon: '👔' },
    { label: 'Hiring', value: signals.hiring_trends?.join(', '), icon: '🎯' },
    { label: 'Tech Stack', value: signals.tech_stack_changes, icon: '⚙️' },
    { label: 'News', value: signals.news_mentions?.join('; '), icon: '📰' },
  ];

  return (
    <div className="bg-slate-800 p-6 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Buyer Signals</h3>
        <span className="bg-blue-600 text-white px-2 py-1 rounded text-sm">
          {signals.raw_signal_count} signals found
        </span>
      </div>
      
      <div className="space-y-4">
        {signalItems.map((item, index) => (
          <div key={index} className="border-l-2 border-slate-600 pl-4">
            <div className="flex items-center space-x-2 mb-1">
              <span>{item.icon}</span>
              <span className="font-medium text-sm">{item.label}</span>
            </div>
            <p className="text-slate-300 text-sm">
              {item.value || 'Not found'}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}