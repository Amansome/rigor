"use client";

import { useEffect, useState } from "react";
import { api, Run, Model, CompareResult } from "@/lib/api";

function fmt(n: number) {
  return n.toFixed(4);
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-surface rounded-md px-4 py-3 space-y-1">
      <p className="text-[12px] text-muted">{label}</p>
      <p className="text-[18px] font-medium text-ink tabular-nums">{value}</p>
      {sub && <p className="text-[11px] text-faint font-mono truncate">{sub}</p>}
    </div>
  );
}

export default function ComparePage() {
  const [runs, setRuns]     = useState<Run[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [runA, setRunA]     = useState("");
  const [runB, setRunB]     = useState("");
  const [metric, setMetric] = useState("pass_at_1");
  const [result, setResult] = useState<CompareResult | null>(null);
  const [error, setError]   = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([api.runs(), api.models()]).then(([r, m]) => {
      setRuns(r.filter((x) => x.status === "completed"));
      setModels(m);
    });
  }, []);

  const modelById = Object.fromEntries(models.map((m) => [m.id, m]));

  function label(run: Run) {
    const m = modelById[run.model_id];
    return m ? `${m.name} — ${run.id.slice(0, 8)}` : run.id.slice(0, 8);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!runA || !runB) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.compare(runA, runB, metric));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const perm   = result?.tests.paired_permutation;
  const wilcox = result?.tests.wilcoxon_signed_rank;
  const sig    = perm?.significant_at_0_05;

  const selectClass =
    "w-full border border-rim rounded-md px-3 py-2 text-[13px] text-ink bg-card focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40";

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
      <div>
        <h1 className="text-[18px] font-medium text-ink">Compare runs</h1>
        <p className="text-[13px] text-muted mt-0.5">
          Paired significance tests between two completed runs
        </p>
      </div>

      <div className="bg-card border border-rim rounded-lg overflow-hidden">
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-[12px] text-muted block">Run A</label>
              <select
                value={runA}
                onChange={(e) => setRunA(e.target.value)}
                className={selectClass}
                required
              >
                <option value="">Select a run…</option>
                {runs.map((r) => (
                  <option key={r.id} value={r.id}>{label(r)}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[12px] text-muted block">Run B</label>
              <select
                value={runB}
                onChange={(e) => setRunB(e.target.value)}
                className={selectClass}
                required
              >
                <option value="">Select a run…</option>
                {runs.map((r) => (
                  <option key={r.id} value={r.id}>{label(r)}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-[12px] text-muted block">Metric</label>
            <input
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
              className="border border-rim rounded-md px-3 py-2 text-[13px] text-ink bg-card w-48 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
              placeholder="pass_at_1"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="cursor-pointer bg-accent/10 border border-accent/20 text-accent text-[13px] font-medium px-4 py-2 rounded-md transition-colors duration-150 hover:bg-accent/15 disabled:opacity-40 disabled:cursor-default focus-visible:ring-2 focus-visible:ring-accent/40 min-h-[44px]"
          >
            {loading ? "Computing…" : "Compare"}
          </button>
        </form>

        {error && (
          <div className="px-6 pb-5">
            <p className="text-fail text-[13px]">{error}</p>
          </div>
        )}
      </div>

      {result && perm && wilcox && (
        <div className="bg-card border border-rim rounded-lg overflow-hidden space-y-0">
          {/* Means */}
          <div className="px-6 py-5 border-b border-rim">
            <h2 className="text-[14px] font-medium text-muted mb-4">Results</h2>
            <div className="grid grid-cols-2 gap-3 mb-4">
              <StatCard
                label="Run A mean"
                value={fmt(result.mean_a)}
                sub={result.run_a.slice(0, 8)}
              />
              <StatCard
                label="Run B mean"
                value={fmt(result.mean_b)}
                sub={result.run_b.slice(0, 8)}
              />
            </div>
            <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-1 text-[13px] max-w-sm">
              <dt className="text-muted">Metric</dt>
              <dd className="font-mono text-ink">{result.metric}</dd>
              <dt className="text-muted">Pairs compared</dt>
              <dd className="tabular-nums text-ink">{result.n_pairs}</dd>
              <dt className="text-muted">Mean difference (A − B)</dt>
              <dd
                className={`tabular-nums font-medium ${
                  result.mean_difference >= 0 ? "text-ok" : "text-fail"
                }`}
              >
                {result.mean_difference >= 0 ? "+" : ""}
                {fmt(result.mean_difference)}
              </dd>
            </dl>
          </div>

          {/* Test table */}
          <div className="px-6 py-5 border-b border-rim">
            <h2 className="text-[14px] font-medium text-muted mb-3">
              Significance tests
            </h2>
            <table className="w-full border-collapse text-[13px]">
              <thead>
                <tr className="border-b border-rim">
                  <th className="pb-2 text-left text-[12px] font-medium text-muted pr-8">
                    Test
                  </th>
                  <th className="pb-2 text-right text-[12px] font-medium text-muted pr-8">
                    p-value
                  </th>
                  <th className="pb-2 text-right text-[12px] font-medium text-muted pr-8">
                    Pairs
                  </th>
                  <th className="pb-2 text-right text-[12px] font-medium text-muted">
                    Significant at 0.05
                  </th>
                </tr>
              </thead>
              <tbody>
                {[perm, wilcox].map((t) => (
                  <tr key={t.test_name} className="border-b border-rim last:border-0">
                    <td className="py-2 pr-8 font-mono text-[12px] text-ink">
                      {t.test_name}
                    </td>
                    <td className="py-2 pr-8 text-right tabular-nums text-ink">
                      {fmt(t.p_value)}
                    </td>
                    <td className="py-2 pr-8 text-right tabular-nums text-ink">
                      {t.n_pairs}
                    </td>
                    <td
                      className={`py-2 text-right font-medium ${
                        t.significant_at_0_05 ? "text-ok" : "text-muted"
                      }`}
                    >
                      {t.significant_at_0_05 ? "Yes" : "No"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Verdict */}
          <div className="px-6 py-4">
            <p
              className={`text-[13px] font-medium ${
                sig ? "text-ok" : "text-warn"
              }`}
            >
              {sig
                ? "Significant at 0.05 — the difference is unlikely due to chance."
                : "Not significant at 0.05 — cannot rule out chance."}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
