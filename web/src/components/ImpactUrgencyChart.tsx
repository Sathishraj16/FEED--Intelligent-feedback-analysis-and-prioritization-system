"use client";

import { FeedbackRow } from "@/lib/api";
import {
  ResponsiveContainer,
  ScatterChart,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  Scatter,
} from "recharts";

function colorBySentiment(s: number | null | undefined): string {
  const v = s ?? 0;
  if (v >= 0.2) return "#10b981"; // green
  if (v <= -0.2) return "#ef4444"; // red
  return "#f59e0b"; // amber
}

export default function ImpactUrgencyChart({ data }: { data: FeedbackRow[] }) {
  const points = (data || [])
    .filter((d) => d.priority != null && d.urgency != null && d.impact != null)
    .map((d) => ({
      id: d.id,
      x: d.urgency as number,
      y: d.impact as number,
      z: Math.max(6, Math.round(((d.priority as number) || 0) * 24 + 6)),
      color: colorBySentiment(d.sentiment),
      text: d.raw_text,
    }));

  return (
    <div className="rounded-2xl border border-neutral-200 bg-white/70 backdrop-blur p-4 shadow-sm">
      <div className="mb-2 text-sm font-medium text-slate-700">Impact vs Urgency</div>
      <div className="h-64 w-full">
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
            <XAxis type="number" dataKey="x" name="Urgency" domain={[0, 1]} tickCount={6} />
            <YAxis type="number" dataKey="y" name="Impact" domain={[0, 1]} tickCount={6} />
            <ZAxis type="number" dataKey="z" range={[6, 30]} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} formatter={(v: any, n: any, p: any) => {
              if (n === "z") return ["priority size", "size"];
              return [v, n];
            }} contentStyle={{ fontSize: 12 }} labelFormatter={() => ""} />
            <Scatter data={points} shape={(props: any) => {
              const { cx, cy, node } = props;
              const fill = node?.payload?.color || "#8884d8";
              const r = node?.payload?.z || 8;
              return <circle cx={cx} cy={cy} r={r} fill={fill} fillOpacity={0.7} />;
            }} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
