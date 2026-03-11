"use client";

interface EmailPreviewProps {
  subject: string;
  body: string;
  sendStatus: boolean;
  sendMessage: string;
}

export default function EmailPreview({ subject, body, sendStatus, sendMessage }: EmailPreviewProps) {
  return (
    <div className="bg-slate-800 p-6 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Email Preview</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          sendStatus 
            ? 'bg-green-600 text-white' 
            : 'bg-red-600 text-white'
        }`}>
          {sendStatus ? '✅ Sent' : '⚠️ Not Sent'}
        </span>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">
            Subject
          </label>
          <p className="font-semibold text-white bg-slate-700 p-3 rounded">
            {subject}
          </p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">
            Body
          </label>
          <div className="bg-slate-700 p-4 rounded">
            <p className="text-slate-200 whitespace-pre-line leading-relaxed">
              {body}
            </p>
          </div>
        </div>
        
        <div className="pt-2 border-t border-slate-600">
          <p className="text-sm text-slate-400">
            <span className="font-medium">Send Status:</span> {sendMessage}
          </p>
        </div>
      </div>
    </div>
  );
}