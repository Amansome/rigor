import Link from "next/link";
import { api, Model, MetricCI } from "@/lib/api";
import CIBar from "./CIBar";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

function duration(start: string | null, end: string | null) {
  if (!start || !end) return "—";
  const ms = new Date(end).getTime() - new Date(start).getTime();
  return `${(ms / 1000).toFixed(1)}s`;
}

function StatusPill({ status }: { status: string }) {
  const styles: Record<string, string> = {
    completed: "bg-ok-tint text-ok",
    pending:   "bg-warn-tint text-warn",
    failed:    "bg-fail-tint text-fail",
    running:   "bg-run-tint text-run",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium ${styles[status] ?? "bg-surface text-muted"}`}>
      {status}
    </span>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface ring-1 ring-rim rounded-md px-4 py-3 space-y-1">
      <p className="text-[12px] text-muted">{label}</p>
      <p className="text-[18px] font-medium text-ink tabular-nums">{value}</p>
    </div>
  );
}

function MetricRow({ name, ci }: { name: string; ci: MetricCI }) {
  return (
    <div className="flex items-center gap-4">
      <span className="font-mono text-[13px] text-muted w-44 shrink-0">{name}</span>
      <CIBar mean={ci.mean} ci_low={ci.ci_low} ci_high={ci.ci_high} />
      <span className="text-[13px] text-ink tabular-nums w-52 shrink-0 text-right">
        {ci.mean.toFixed(3)}{" "}
        <span className="text-faint">[{ci.ci_low.toFixed(3)}, {ci.ci_high.toFixed(3)}]</span>
      </span>
    </div>
  );
}

export default async function RunDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const [run, summary, models] = await Promise.all([api.run(id), api.summary(id), api.models()]);

  const [datasetsData, promptsData] = await Promise.all([
    fetch(`${API_BASE}/datasets`, { cache: "no-store" }).then((r) => r.json()).catch(() => []),
    fetch(`${API_BASE}/prompts`,  { cache: "no-store" }).then((r) => r.json()).catch(() => []),
  ]);

  const model: Model | undefined = models.find((m) => m.id === run.model_id);
  const dataset = datasetsData.find((d: { id: string; name: string }) => d.id === run.dataset_id);
  const prompt  = promptsData.find((p: { id: string; name: string; version: number }) => p.id === run.prompt_id);
  const metrics  = Object.entries(summary.metrics);
  const nSamples = metrics[0]?.[1]?.n_samples ?? summary.n_results;
  const passAt1  = summary.metrics?.pass_at_1?.mean;

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <Link href="/" className="text-[12px] text-faint hover:text-ink transition-colors duration-150 inline-block">
        ← All runs
      </Link>

      <div className="bg-card border border-rim rounded-lg overflow-hidden">
        <div className="px-6 py-5 border-b border-rim">
          <div className="flex items-center justify-between">
            <h1 className="font-mono text-[18px] font-medium text-ink">run/{id.slice(0, 8)}</h1>
            <StatusPill status={run.status} />
          </div>
          <p className="font-mono text-[13px] text-muted mt-1.5">
            {model?.name ?? run.model_id.slice(0, 8)}
            {dataset && <> · {dataset.name}</>}
            {prompt  && <> · {prompt.name} v{prompt.version}</>}
          </p>
        </div>

        <div className="px-6 py-5 border-b border-rim grid grid-cols-4 gap-3">
          <StatCard label="Examples" value={String(summary.n_results)} />
          <StatCard label="Errors"   value={String(summary.n_errors)} />
          <StatCard label="Duration" value={duration(run.started_at, run.completed_at)} />
          <StatCard label="Pass@1"   value={passAt1 != null ? passAt1.toFixed(3) : "—"} />
        </div>

        <div className="px-6 py-5">
          <h2 className="text-[14px] font-medium text-muted mb-4">
            Metrics (95% bootstrap CI, n={nSamples})
          </h2>
          {metrics.length === 0 ? (
            <p className="text-[13px] text-faint">No metrics recorded.</p>
          ) : (
            <div className="space-y-3">
              {metrics.map(([name, ci]) => <MetricRow key={name} name={name} ci={ci} />)}
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-rim">
          <Link href="/compare" className="text-[12px] text-faint hover:text-ink transition-colors duration-150">
            Compare this run with another →
          </Link>
        </div>
      </div>
    </div>
  );
}
