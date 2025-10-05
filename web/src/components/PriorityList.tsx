'use client';

import { useEffect, useMemo, useState } from "react";
import { prioritized, type FeedbackRow } from "@/lib/api";

type TagOption =
  | "bug"
  | "feature_request"
  | "billing"
  | "negative"
  | "neutral"
  | "very_positive";

const TAGS: TagOption[] = ["bug","feature_request","billing","negative","neutral","very_positive"];

function num(n: number | null | undefined, digits = 2) {
  if (n === null || n === undefined) return "—";
  return n.toFixed(digits);
}

export default function PriorityList({ reloadKey = 0 }: { reloadKey?: number }) {
  const [rows, setRows] = useState<FeedbackRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // filters
  const [q, setQ] = useState("");
  const [minPriority, setMinPriority] = useState(0);
  const [tag, setTag] = useState<TagOption | "">("");

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const data = await prioritized(50);
      const clean = (data || [])
        .filter(r => r.priority !== null && r.priority !== undefined)
        .sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0));
      setRows(clean);
    } catch (e: any) {
      setErr(e?.message || "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);
  useEffect(() => { if (reloadKey > 0) load(); }, [reloadKey]);

  const filtered = useMemo(() => {
    let out = rows.slice();
    if (q.trim()) {
      const qq = q.trim().toLowerCase();
      out = out.filter(r => r.raw_text.toLowerCase().includes(qq));
    }
    if (tag) {
      out = out.filter(r => (r.tags || []).includes(tag));
    }
    if (minPriority > 0) {
      out = out.filter(r => (r.priority ?? 0) >= minPriority);
    }
    return out;
  }, [rows, q, tag, minPriority]);

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div className="relative">
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">🔎</span>
          <input
            className="w-full border border-neutral-300 rounded-full bg-white pl-9 pr-4 py-2 text-[14px] focus:outline-none focus:ring-2 focus:ring-neutral-300 placeholder:text-slate-400"
            placeholder="Search text…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <div className="border border-neutral-300 rounded-full px-3 py-2 flex items-center gap-2 bg-white">
          <label className="whitespace-nowrap text-sm text-slate-700">Min priority</label>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={minPriority}
            onChange={(e) => setMinPriority(parseFloat(e.target.value))}
            className="w-full accent-black"
          />
          <span className="w-12 text-right text-sm tabular-nums">{num(minPriority, 2)}</span>
        </div>
        <select
          className="border border-neutral-300 rounded-full px-3 py-2 bg-white text-[14px] focus:outline-none focus:ring-2 focus:ring-neutral-300"
          value={tag}
          onChange={(e) => setTag(e.target.value as any)}
        >
          <option value="">All tags</option>
          {TAGS.map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <button
          onClick={load}
          className="inline-flex items-center justify-center rounded-full border border-neutral-300 bg-white px-4 py-2 hover:bg-neutral-50 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {err && <div className="border border-red-200 rounded-lg p-3 text-red-700 bg-red-50">{err}</div>}

      <ul className="space-y-3">
        {filtered.map((r) => (
          <li key={r.id} className="border border-neutral-300 rounded-xl p-4 bg-white shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all">
            <div className="flex items-start justify-between gap-3">
              <div className="text-xs text-gray-500">#{r.id}</div>
              <div className="text-xs text-gray-500">{new Date(r.created_at).toLocaleString()}</div>
            </div>

            <p className="mt-2 text-[15px] leading-6">{r.raw_text}</p>

            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
              <Chip label={`priority ${num(r.priority)}`} kind="metric" />
              <Chip label={`urg ${num(r.urgency)}`} kind="metric" />
              <Chip label={`impact ${num(r.impact)}`} kind="metric" />
              <Chip label={`sent ${num(r.sentiment)}`} kind="metric" />
              {(r.tags || []).map(t => <Chip key={t} label={t} kind={tagToKind(t)} />)}
              {r.source && <Chip label={`src:${r.source}`} />}
            </div>
          </li>
        ))}

        {!loading && filtered.length === 0 && (
          <div className="border border-neutral-200 rounded-xl p-4 text-sm text-gray-600 bg-gray-50">
            No items match your filters. Try lowering min priority or clearing tag/search.
          </div>
        )}
      </ul>
    </div>
  );
}

type ChipKind = "default" | "metric" | "bug" | "feature" | "billing" | "sentiment-negative" | "sentiment-neutral" | "sentiment-positive";

function tagToKind(tag: string): ChipKind {
  if (tag === "bug") return "bug";
  if (tag === "feature_request") return "feature";
  if (tag === "billing") return "billing";
  if (tag === "negative") return "sentiment-negative";
  if (tag === "neutral") return "sentiment-neutral";
  if (tag === "very_positive") return "sentiment-positive";
  return "default";
}

function Chip({ label, kind = "default" }: { label: string; kind?: ChipKind }) {
  const cls = (() => {
    switch (kind) {
      case "metric":
        return "border-neutral-200 bg-white";
      case "bug":
        return "border-red-200 bg-red-50 text-red-800";
      case "feature":
        return "border-blue-200 bg-blue-50 text-blue-800";
      case "billing":
        return "border-amber-200 bg-amber-50 text-amber-900";
      case "sentiment-negative":
        return "border-rose-200 bg-rose-50 text-rose-800";
      case "sentiment-neutral":
        return "border-neutral-200 bg-neutral-100 text-neutral-700";
      case "sentiment-positive":
        return "border-emerald-200 bg-emerald-50 text-emerald-800";
      default:
        return "border-neutral-200 bg-white";
    }
  })();
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-1 ${cls}`}>{label}</span>
  );
}

