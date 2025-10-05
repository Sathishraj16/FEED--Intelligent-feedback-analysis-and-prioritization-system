"use client";

import { Kpis } from "@/lib/api";

export default function DashboardKpis({ kpis }: { kpis: Kpis | null }) {
  const cards = [
    { label: "Total Feedbacks", value: kpis?.total ?? 0 },
    { label: "Urgent Issues", value: kpis?.urgent ?? 0 },
    { label: "Positive", value: kpis?.positive ?? 0 },
    { label: "Negative", value: kpis?.negative ?? 0 },
    { label: "Avg Priority", value: (kpis?.avg_priority ?? 0).toFixed(2) },
  ];
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4 mb-4">
      {cards.map((c) => (
        <div key={c.label} className="rounded-2xl border border-neutral-200 bg-white/70 backdrop-blur p-4 shadow-sm">
          <div className="text-xs uppercase tracking-wide text-slate-500">{c.label}</div>
          <div className="mt-1 text-2xl font-semibold text-slate-900">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
