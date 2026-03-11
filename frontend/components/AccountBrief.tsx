"use client";

interface AccountBriefProps {
  brief: string;
}

export default function AccountBrief({ brief }: AccountBriefProps) {
  return (
    <div className="bg-slate-800 p-6 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Account Brief</h3>
      <div className="prose prose-invert max-w-none">
        <p className="text-slate-300 leading-relaxed whitespace-pre-line">
          {brief}
        </p>
      </div>
    </div>
  );
}