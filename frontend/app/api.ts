const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface OutreachRequest {
  icp: string;
  target_company: string;
  recipient_email: string;
  sender_name: string;
}

export interface SignalData {
  funding_rounds: string | null;
  leadership_changes: string | null;
  hiring_trends: string[];
  tech_stack_changes: string | null;
  news_mentions: string[];
  raw_signal_count: number;
}

export interface OutreachResponse {
  success: boolean;
  signals: SignalData;
  account_brief: string;
  email_subject: string;
  email_body: string;
  send_status: boolean;
  send_message: string;
  execution_log: string[];
  error?: string;
}

export async function runOutreach(payload: OutreachRequest): Promise<OutreachResponse> {
  const res = await fetch(`${API_URL}/api/outreach`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Agent failed");
  }
  return res.json();
}