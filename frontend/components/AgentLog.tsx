"use client";

interface AgentLogProps {
  logs: string[];
}

export default function AgentLog({ logs }: AgentLogProps) {
  return (
    <div className="bg-slate-800 p-6 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Agent Execution Log</h3>
      <div className="space-y-2">
        {logs.map((log, index) => (
          <div key={index} className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <span className="text-slate-300 text-sm">{log}</span>
          </div>
        ))}
      </div>
    </div>
  );
}