"use client";

import { useEffect, useMemo, useState } from "react";
import { prioritized, type FeedbackRow, summarizeById, suggestReplyById } from "@/lib/api";

function num(n: number | null | undefined, digits = 2) {
  if (n === null || n === undefined) return "—";
  return n.toFixed(digits);
}

const TAGS = ["", "bug", "feature_request", "billing", "negative", "neutral", "very_positive"] as const;

type Tag = typeof TAGS[number];

export default function PriorityTable() {
  const [rows, setRows] = useState<FeedbackRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [summaryBusy, setSummaryBusy] = useState<Record<number, boolean>>({});
  const [replyBusy, setReplyBusy] = useState<Record<number, boolean>>({});
  const [replyShown, setReplyShown] = useState<Record<number, string | null>>({});

  // filters
  const [q, setQ] = useState("");
  const [minPriority, setMinPriority] = useState(0);
  const [tag, setTag] = useState<Tag>("");

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const data = await prioritized(50);
      const clean = (data || [])
        .filter((r) => r.priority !== null && r.priority !== undefined)
        .sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0));
      setRows(clean);
    } catch (e: any) {
      setErr(e?.message || "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    let out = rows.slice();
    if (q.trim()) {
      const qq = q.trim().toLowerCase();
      out = out.filter((r) => r.raw_text.toLowerCase().includes(qq));
    }
    if (tag) out = out.filter((r) => (r.tags || []).includes(tag));
    if (minPriority > 0) out = out.filter((r) => (r.priority ?? 0) >= minPriority);
    return out;
  }, [rows, q, tag, minPriority]);

  return (
    <div className="flex flex-col md:flex-row gap-3 md:gap-6">
      {/* Sidebar filters */}
      <aside className="w-full md:w-72 lg:w-80">
        <div className="flex flex-col gap-6">
          {/* Search */}
          <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-lg font-bold text-slate-900">🔍 Search & Filter</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3 rounded-lg border border-neutral-300 bg-slate-50 px-4 py-3">
                <span className="text-slate-500">🔎</span>
                <input
                  className="w-full bg-transparent border-0 outline-none placeholder:text-slate-400 text-slate-900"
                  placeholder="Search feedback content..."
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  suppressHydrationWarning
                />
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-slate-700" htmlFor="min-priority">
                    ⚡ Min Priority
                  </label>
                  <span className="text-sm font-bold text-slate-900 bg-slate-100 px-2 py-1 rounded-md">
                    {Math.round(minPriority * 100)}%
                  </span>
                </div>
                <input
                  className="h-3 w-full cursor-pointer appearance-none rounded-lg bg-gray-200 accent-black"
                  id="min-priority"
                  type="range"
                  min={0}
                  max={1}
                  step={0.01}
                  value={minPriority}
                  onChange={(e) => setMinPriority(parseFloat(e.target.value))}
                />
                <div className="flex justify-between text-xs text-slate-500">
                  <span>Low</span>
                  <span>Medium</span>
                  <span>High</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  🏷️ Filter by Tag
                </label>
                <select
                  className="w-full rounded-lg border border-neutral-300 bg-white py-3 pl-4 pr-10 text-slate-900 focus:border-black focus:ring-1 focus:ring-black transition-all"
                  value={tag}
                  onChange={(e) => setTag(e.target.value as Tag)}
                  suppressHydrationWarning
                >
                  <option value="">All Tags</option>
                  {TAGS.filter((t) => t).map((t) => (
                    <option key={t} value={t as string}>
                      {t.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={load}
                className="flex w-full items-center justify-center gap-3 rounded-lg bg-black py-3 text-sm font-semibold text-white hover:bg-gray-800 disabled:opacity-50 transition-all duration-200"
                disabled={loading}
                suppressHydrationWarning
              >
                {loading ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    <span>Refreshing...</span>
                  </>
                ) : (
                  <>
                    <span className="text-lg">🔄</span>
                    <span>Refresh Data</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
            <h4 className="mb-4 text-lg font-bold text-slate-900">📊 Quick Stats</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-2 rounded-lg bg-slate-50">
                <span className="text-sm font-medium text-slate-600">Total Items</span>
                <span className="font-bold text-slate-900 bg-white px-2 py-1 rounded-md">
                  {filtered.length}
                </span>
              </div>
              <div className="flex justify-between items-center p-2 rounded-lg bg-red-50">
                <span className="text-sm font-medium text-red-700">High Priority</span>
                <span className="font-bold text-red-800 bg-white px-2 py-1 rounded-md">
                  {filtered.filter(r => (r.priority ?? 0) >= 0.66).length}
                </span>
              </div>
              <div className="flex justify-between items-center p-2 rounded-lg bg-amber-50">
                <span className="text-sm font-medium text-amber-700">Negative Sentiment</span>
                <span className="font-bold text-amber-800 bg-white px-2 py-1 rounded-md">
                  {filtered.filter(r => (r.sentiment ?? 0) <= -0.2).length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Table */}
      <section className="flex-1 min-w-0">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-slate-900">Prioritized Feedback</h2>
            <div className="text-sm text-slate-500">
              {filtered.length} {filtered.length === 1 ? 'item' : 'items'}
            </div>
          </div>

          <div className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-neutral-200">
              <thead className="bg-gradient-to-r from-slate-50 to-neutral-50">
                <tr>
                  <Th className="w-16">ID</Th>
                  <Th className="w-24">Date</Th>
                  <Th className="w-80">Feedback</Th>
                  <Th className="w-72">AI Summary</Th>
                  <Th className="w-20">Priority</Th>
                  <Th className="w-20">Urgency</Th>
                  <Th className="w-20">Impact</Th>
                  <Th className="w-24">Sentiment</Th>
                  <Th className="w-32">Tags</Th>
                  <Th className="w-20">Source</Th>
                  <Th className="w-80">Actions</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {err && (
                  <tr>
                    <td colSpan={11} className="px-8 py-6 text-sm text-red-700 bg-red-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        <span className="text-red-500">⚠️</span>
                        {err}
                      </div>
                    </td>
                  </tr>
                )}
                {filtered.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/50 transition-colors duration-150">
                    <Td className="font-semibold text-slate-900">#{r.id}</Td>
                    <Td className="text-slate-600">{new Date(r.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</Td>
                    <Td className="max-w-[320px]">
                      <div className="text-slate-700 leading-relaxed" title={r.raw_text}>
                        {r.raw_text.length > 120 ? r.raw_text.substring(0, 120) + '...' : r.raw_text}
                      </div>
                    </Td>
                    <Td className="max-w-[280px]">
                      {r.summary ? (
                        <div className="text-slate-700 leading-relaxed" title={r.summary}>
                          {r.summary.length > 100 ? r.summary.substring(0, 100) + '...' : r.summary}
                        </div>
                      ) : (
                        <button
                          onClick={async () => {
                            setSummaryBusy((m) => ({ ...m, [r.id]: true }));
                            try {
                              const { summary } = await summarizeById(r.id);
                              setRows((rows) => rows.map((x) => x.id === r.id ? { ...x, summary } : x));
                            } catch (e: any) {
                              alert(e?.message || "Failed to summarize");
                            } finally {
                              setSummaryBusy((m) => ({ ...m, [r.id]: false }));
                            }
                          }}
                          disabled={!!summaryBusy[r.id]}
                          className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50 transition-colors"
                        >
                          {summaryBusy[r.id] ? (
                            <>
                              <div className="animate-spin h-3 w-3 border border-gray-400 border-t-transparent rounded-full"></div>
                              Generating...
                            </>
                          ) : (
                            <>
                              <span>✨</span>
                              Generate Summary
                            </>
                          )}
                        </button>
                      )}
                    </Td>
                    <Td>
                      <span title={`Priority derived from urgency=${num(r.urgency)} & impact=${num(r.impact)} (sentiment=${num(r.sentiment)})`}>
                        <Pill color={priorityColor(r.priority)} size="sm">{level(r.priority)}</Pill>
                      </span>
                    </Td>
                    <Td><Pill color="orange" size="sm">{level(r.urgency)}</Pill></Td>
                    <Td><Pill color="red" size="sm">{level(r.impact)}</Pill></Td>
                    <Td><Pill color={sentimentColor(r.sentiment)} size="sm">{sentimentLabel(r.sentiment)}</Pill></Td>
                    <Td>
                      <div className="flex flex-wrap gap-1.5">
                        {(r.tags || []).slice(0, 3).map((t) => (
                          <span key={t} className="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700 border border-slate-200">
                            {t}
                          </span>
                        ))}
                        {(r.tags || []).length > 3 && (
                          <span className="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500 border border-slate-200">
                            +{(r.tags || []).length - 3}
                          </span>
                        )}
                      </div>
                    </Td>
                    <Td>
                      <span className="inline-flex items-center rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700 border border-slate-200">
                        {r.source || "manual"}
                      </span>
                    </Td>
                    <Td className="w-80">
                      <div className="flex flex-col gap-2">
                        <button
                          onClick={async () => {
                            setReplyBusy((m) => ({ ...m, [r.id]: true }));
                            try {
                              const { reply } = await suggestReplyById(r.id);
                              setReplyShown((m) => ({ ...m, [r.id]: reply }));
                            } catch (e: any) {
                              alert(e?.message || "Failed to suggest reply");
                            } finally {
                              setReplyBusy((m) => ({ ...m, [r.id]: false }));
                            }
                          }}
                          disabled={!!replyBusy[r.id]}
                          className="inline-flex items-center gap-2 rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-all duration-200"
                        >
                          {replyBusy[r.id] ? (
                            <>
                              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                              Analyzing...
                            </>
                          ) : (
                            <>
                              <span>🎯</span>
                              Analyze Action
                            </>
                          )}
                        </button>
                        {replyShown[r.id] && (
                          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm">
                            <div className="mb-2 flex items-center justify-between">
                              <div className="font-semibold text-gray-900">Action Analysis</div>
                              <button
                                onClick={() => setReplyShown((m) => ({ ...m, [r.id]: null }))}
                                className="rounded-md p-1 text-gray-600 hover:bg-gray-100 transition-colors"
                              >
                                ✕
                              </button>
                            </div>
                            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">{replyShown[r.id]}</div>
                          </div>
                        )}
                      </div>
                    </Td>
                  </tr>
                ))}
                {!loading && filtered.length === 0 && !err && (
                  <tr>
                    <td colSpan={11} className="px-8 py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <div className="text-4xl">📋</div>
                        <div className="text-lg font-medium text-slate-600">No feedback found</div>
                        <div className="text-sm text-slate-500">Try adjusting your filters or check back later</div>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}

function Th({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <th scope="col" className={`px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-600 ${className}`}>
      {children}
    </th>
  );
}

function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <td className={`px-6 py-4 text-sm text-slate-600 ${className}`}>{children}</td>
  );
}

function Pill({ children, color, size = "md" }: { children: React.ReactNode; color: "red" | "orange" | "green" | "blue" | "purple"; size?: "sm" | "md" }) {
  const colorMap: Record<string, string> = {
    red: "bg-red-100 text-red-800 border-red-200",
    orange: "bg-amber-100 text-amber-800 border-amber-200",
    green: "bg-emerald-100 text-emerald-800 border-emerald-200",
    blue: "bg-gray-100 text-gray-800 border-gray-200",
    purple: "bg-gray-100 text-gray-800 border-gray-200",
  };
  const sizeMap = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-1 text-sm"
  };
  return (
    <span className={`inline-flex items-center rounded-full font-medium border ${colorMap[color]} ${sizeMap[size]}`}>
      {children}
    </span>
  );
}

function level(v?: number | null) {
  const n = v ?? 0;
  if (n >= 0.66) return "High";
  if (n >= 0.33) return "Medium";
  return "Low";
}

function sentimentLabel(v?: number | null) {
  const n = v ?? 0;
  if (n >= 0.2) return "Positive";
  if (n <= -0.2) return "Negative";
  return "Neutral";
}

function sentimentColor(v?: number | null): "green" | "red" | "orange" {
  const n = v ?? 0;
  if (n >= 0.2) return "green";
  if (n <= -0.2) return "red";
  return "orange";
}

function priorityColor(v?: number | null): "red" | "orange" | "green" | "blue" | "purple" {
  const n = v ?? 0;
  if (n >= 0.8) return "red";
  if (n >= 0.6) return "orange";
  if (n >= 0.4) return "purple";
  return "green";
}
