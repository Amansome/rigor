import Link from "next/link";
import { api } from "@/lib/api";
import MetricsChart from "./MetricsChart";

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
}

function duration(start: string | null, end: string | null) {
  if (!start || !end) return "—";
  const ms = new Date(end).getTime() - new Date(start).getTime();
  return `${(ms / 1000).toFixed(1)}s`;
}

export default async function RunDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [run, summary] = await Promise.all([api.run(id), api.summary(id)]);

  const metrics = Object.entries(summary.metrics);

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
      <div>
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          ← All runs
        </Link>
        <h1 className="text-xl font-medium text-gray-900 mt-2">Run detail</h1>
        <p className="font-mono text-xs text-gray-400 mt-1">{id}</p>
      </div>

      <section className="space-y-2 text-sm">
        <h2 className="font-medium text-gray-700">Metadata</h2>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-gray-600">
          <dt className="text-gray-400">Status</dt>
          <dd>{run.status}</dd>
          <dt className="text-gray-400">Started</dt>
          <dd>{formatDate(run.started_at)}</dd>
          <dt className="text-gray-400">Completed</dt>
          <dd>{formatDate(run.completed_at)}</dd>
          <dt className="text-gray-400">Duration</dt>
          <dd>{duration(run.started_at, run.completed_at)}</dd>
          <dt className="text-gray-400">Results</dt>
          <dd>{summary.n_results} ({summary.n_errors} errors)</dd>
        </dl>
      </section>

      <section className="space-y-4 text-sm">
        <h2 className="font-medium text-gray-700">Metrics</h2>
        {metrics.length === 0 ? (
          <p className="text-gray-400">No metrics recorded.</p>
        ) : (
          <div className="space-y-4">
            {metrics.map(([name, ci]) => (
              <div key={name} className="space-y-1">
                <div className="flex items-baseline gap-3">
                  <span className="font-mono text-gray-700">{name}</span>
                  <span className="text-gray-500">
                    {ci.mean.toFixed(3)} [{ci.ci_low.toFixed(3)}, {ci.ci_high.toFixed(3)}]
                  </span>
                  <span className="text-gray-400 text-xs">n={ci.n_samples}</span>
                </div>
              </div>
            ))}
            <MetricsChart metrics={summary.metrics} />
          </div>
        )}
      </section>

      <section className="text-sm">
        <Link href="/compare" className="text-blue-600 hover:underline">
          Compare this run with another →
        </Link>
      </section>
    </div>
  );
}
