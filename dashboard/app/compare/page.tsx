"use client";

import { useEffect, useState } from "react";
import { api, Run, Model, CompareResult } from "@/lib/api";

function fmt(n: number) {
  return n.toFixed(4);
}

export default function ComparePage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [runA, setRunA] = useState("");
  const [runB, setRunB] = useState("");
  const [metric, setMetric] = useState("pass_at_1");
  const [result, setResult] = useState<CompareResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([api.runs(), api.models()]).then(([r, m]) => {
      const completed = r.filter((x) => x.status === "completed");
      setRuns(completed);
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
      const r = await api.compare(runA, runB, metric);
      setResult(r);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const perm = result?.tests.paired_permutation;
  const wilcox = result?.tests.wilcoxon_signed_rank;

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
      <div>
        <h1 className="text-xl font-medium text-gray-900">Compare runs</h1>
        <p className="text-sm text-gray-500 mt-1">Paired significance tests between two completed runs</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 text-sm">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-gray-500">Run A</label>
            <select
              value={runA}
              onChange={(e) => setRunA(e.target.value)}
              className="w-full border border-gray-200 rounded px-2 py-1.5 text-gray-700 bg-white"
              required
            >
              <option value="">Select a run…</option>
              {runs.map((r) => (
                <option key={r.id} value={r.id}>{label(r)}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-gray-500">Run B</label>
            <select
              value={runB}
              onChange={(e) => setRunB(e.target.value)}
              className="w-full border border-gray-200 rounded px-2 py-1.5 text-gray-700 bg-white"
              required
            >
              <option value="">Select a run…</option>
              {runs.map((r) => (
                <option key={r.id} value={r.id}>{label(r)}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-gray-500">Metric</label>
          <input
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="border border-gray-200 rounded px-2 py-1.5 text-gray-700 bg-white w-48"
            placeholder="pass_at_1"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white text-sm px-4 py-1.5 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Computing…" : "Compare"}
        </button>
      </form>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {result && perm && wilcox && (
        <div className="space-y-6 text-sm">
          <section className="space-y-2">
            <h2 className="font-medium text-gray-700">Summary</h2>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-gray-600 max-w-sm">
              <dt className="text-gray-400">Metric</dt>
              <dd className="font-mono">{result.metric}</dd>
              <dt className="text-gray-400">Pairs compared</dt>
              <dd>{result.n_pairs}</dd>
              <dt className="text-gray-400">Mean A</dt>
              <dd>{fmt(result.mean_a)}</dd>
              <dt className="text-gray-400">Mean B</dt>
              <dd>{fmt(result.mean_b)}</dd>
              <dt className="text-gray-400">Mean difference (A − B)</dt>
              <dd className={result.mean_difference >= 0 ? "text-green-700" : "text-red-700"}>
                {result.mean_difference >= 0 ? "+" : ""}{fmt(result.mean_difference)}
              </dd>
            </dl>
          </section>

          <section className="space-y-2">
            <h2 className="font-medium text-gray-700">Significance tests</h2>
            <table className="text-sm border-collapse w-full max-w-lg">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-400">
                  <th className="pb-1 font-medium pr-8">Test</th>
                  <th className="pb-1 font-medium pr-8">p-value</th>
                  <th className="pb-1 font-medium pr-8">Pairs</th>
                  <th className="pb-1 font-medium">Significant at 0.05</th>
                </tr>
              </thead>
              <tbody>
                {[perm, wilcox].map((t) => (
                  <tr key={t.test_name} className="border-b border-gray-100">
                    <td className="py-1.5 pr-8 font-mono text-xs text-gray-700">{t.test_name}</td>
                    <td className="py-1.5 pr-8">{fmt(t.p_value)}</td>
                    <td className="py-1.5 pr-8">{t.n_pairs}</td>
                    <td className={`py-1.5 ${t.significant_at_0_05 ? "text-green-700" : "text-gray-500"}`}>
                      {t.significant_at_0_05 ? "Yes" : "No"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section>
            <p className={`font-medium ${perm.significant_at_0_05 ? "text-green-700" : "text-gray-600"}`}>
              {perm.significant_at_0_05
                ? "Significant at 0.05 — the difference is unlikely due to chance."
                : "Not significant at 0.05 — cannot rule out chance."}
            </p>
          </section>
        </div>
      )}
    </div>
  );
}
