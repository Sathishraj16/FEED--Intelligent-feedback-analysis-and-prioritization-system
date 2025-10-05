"use client";

import { useEffect, useState } from "react";
import PriorityTable from "@/components/PriorityTable";
import DashboardKpis from "@/components/DashboardKpis";
import ImpactUrgencyChart from "@/components/ImpactUrgencyChart";
import SentimentOverTime from "@/components/SentimentOverTime";
import CsvUpload from "@/components/CsvUpload";
import { getKpis, prioritized, type Kpis, type FeedbackRow } from "@/lib/api";

export default function FeedPage() {
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [top, setTop] = useState<FeedbackRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setErr(null);
      try {
        const [k, p] = await Promise.all([getKpis(30), prioritized(50)]);
        setKpis(k);
        setTop((p || []).filter((r) => r.priority != null));
      } catch (e: any) {
        setErr(e?.message || "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <main className="min-h-screen bg-neutral-50">
      <section className="w-full px-4 md:px-6 lg:px-8 py-4 md:py-6 space-y-4">
        {err && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{err}</div>
        )}
        <CsvUpload />
        <DashboardKpis kpis={kpis} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ImpactUrgencyChart data={top} />
          <SentimentOverTime kpis={kpis} />
        </div>
        <PriorityTable />
      </section>
    </main>
  );
}
