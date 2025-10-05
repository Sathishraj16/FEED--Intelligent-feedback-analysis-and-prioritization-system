"use client";

import { Kpis } from "@/lib/api";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export default function SentimentOverTime({ kpis }: { kpis: Kpis | null }) {
  const data = kpis?.sentiment_over_time || [];
  return (
    <div className="rounded-2xl border border-neutral-200 bg-white/70 backdrop-blur p-4 shadow-sm">
      <div className="mb-2 text-sm font-medium text-slate-700">Sentiment Over Time</div>
      <div className="h-64 w-full">
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis domain={[-1, 1]} tick={{ fontSize: 12 }} />
            <Tooltip contentStyle={{ fontSize: 12 }} />
            <Line type="monotone" dataKey="avg_sentiment" stroke="#6366f1" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
