// web/src/lib/api.ts

export type EchoResponse = { you_sent: string; length: number };

export type IngestResponse = { saved: boolean; id: number; priority?: number };

export type FeedbackRow = {
  id: number;
  source: string | null;
  raw_text: string;
  created_at: string;
  text_norm: string | null;
  text_hash: string | null;
  sentiment: number | null;
  urgency: number | null;
  impact: number | null;
  priority: number | null;
  tags: string[] | null;
  summary?: string | null;
  consensus_score?: number | null;
};

const API_BASE = "http://127.0.0.1:8000";

// Test endpoint
export async function echo(text: string): Promise<EchoResponse> {
  const res = await fetch(`${API_BASE}/echo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// Save feedback -> DB (Supabase) and compute scores
export async function ingest(text: string, source = "manual"): Promise<IngestResponse> {
  const res = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, source }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// Recent feedback (by id desc)
export async function listFeedback(limit = 10): Promise<FeedbackRow[]> {
  const res = await fetch(`${API_BASE}/feedback?limit=${limit}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// Prioritized feedback (highest priority first)
export async function prioritized(limit = 20): Promise<FeedbackRow[]> {
  const res = await fetch(`${API_BASE}/prioritized?limit=${limit}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// ---- AI helpers ----
export async function summarizeById(id: number): Promise<{ summary: string }> {
  const res = await fetch(`${API_BASE}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function suggestReplyById(id: number): Promise<{ reply: string }> {
  const res = await fetch(`${API_BASE}/suggest_reply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export type Kpis = {
  total: number;
  urgent: number;
  positive: number;
  negative: number;
  avg_priority: number;
  sentiment_over_time: { date: string; avg_sentiment: number }[];
};

export async function getKpis(days = 30): Promise<Kpis> {
  const res = await fetch(`${API_BASE}/kpis?days=${days}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// CSV Upload types and functions
export type CsvUploadResponse = {
  success: boolean;
  message: string;
  stats: {
    imported: number;
    skipped: number;
    errors: number;
    total_processed: number;
  };
  filename: string;
};

export type ImportStatus = {
  total_feedback: number;
  app_store_reviews: number;
  recent_imports_24h: number;
  other_sources: number;
};

export async function uploadCsv(file: File): Promise<CsvUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_BASE}/upload-csv`, {
    method: "POST",
    body: formData,
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(errorData.detail || `Upload failed with status ${res.status}`);
  }
  
  return res.json();
}

export async function getImportStatus(): Promise<ImportStatus> {
  const res = await fetch(`${API_BASE}/import-status`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
