import Link from "next/link";
import { api, Run, Model, RunSummary } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

function formatCreated(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  if (isToday) return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  return d.toLocaleDateString([], { month: "short", day: "numeric" }) + " " +
    d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
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

export default async function RunsPage() {
  let runs: Run[] = [];
  let models: Model[] = [];
  let summaries: Record<string, RunSummary> = {};
  let error: string | null = null;

  try {
    [runs, models] = await Promise.all([api.runs(), api.models()]);
    const completed = runs.filter((r) => r.status === "completed");
    const results = await Promise.all(completed.map((r) => api.summary(r.id).catch(() => null)));
    completed.forEach((r, i) => { if (results[i]) summaries[r.id] = results[i]!; });
  } catch {
    error = `Could not reach Rigor API at ${API_BASE}. Is the backend running?`;
  }

  const modelById = Object.fromEntries(models.map((m) => [m.id, m]));
  const sorted = [...runs].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  const total = runs.length;
  const nComplete = runs.filter((r) => r.status === "completed").length;
  const nPending  = runs.filter((r) => r.status === "pending").length;

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-5">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-[18px] font-medium text-ink">Runs</h1>
          <p className="text-[13px] text-muted mt-0.5">LLM evaluation and regression results</p>
        </div>
        <span className="text-[12px] text-faint tabular-nums">
          {total} total · {nComplete} completed · {nPending} pending
        </span>
      </div>

      {error ? (
        <p className="text-fail text-[13px]">{error}</p>
      ) : (
        <div className="bg-card border border-rim rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-[13px]">
              <thead>
                <tr className="bg-surface border-b border-rim">
                  <th className="px-4 py-2.5 text-left text-[12px] font-medium text-muted">Model</th>
                  <th className="px-4 py-2.5 text-left text-[12px] font-medium text-muted">Status</th>
                  <th className="px-4 py-2.5 text-right text-[12px] font-medium text-muted">Pass@1</th>
                  <th className="px-4 py-2.5 text-right text-[12px] font-medium text-muted">Created</th>
                  <th className="px-4 py-2.5 w-16" />
                </tr>
              </thead>
              <tbody>
                {sorted.map((run, i) => {
                  const model   = modelById[run.model_id];
                  const summary = summaries[run.id];
                  const passAt1 = summary?.metrics?.pass_at_1?.mean;
                  const isLast  = i === sorted.length - 1;
                  return (
                    <tr
                      key={run.id}
                      className={`relative cursor-pointer transition-colors duration-150 hover:bg-surface ${!isLast ? "border-b border-rim" : ""}`}
                    >
                      <td className="px-4 py-3">
                        <span className="font-mono text-[12px] text-ink">
                          {model?.name ?? run.model_id.slice(0, 8)}
                        </span>
                        {model && <span className="ml-2 text-[11px] text-faint">{model.provider}</span>}
                      </td>
                      <td className="px-4 py-3"><StatusPill status={run.status} /></td>
                      <td className="px-4 py-3 text-right font-mono text-[12px] text-ink tabular-nums">
                        {passAt1 != null ? passAt1.toFixed(3) : "—"}
                      </td>
                      <td className="px-4 py-3 text-right text-[12px] text-muted tabular-nums">
                        {formatCreated(run.created_at)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          href={`/runs/${run.id}`}
                          className="text-[12px] text-faint hover:text-ink transition-colors duration-150 after:absolute after:inset-0 after:content-['']"
                        >
                          View →
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
