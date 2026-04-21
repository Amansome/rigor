import Link from "next/link";
import { api, Run, Model } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString();
}

const STATUS_COLORS: Record<string, string> = {
  completed: "text-green-700",
  running: "text-blue-700",
  pending: "text-gray-500",
  failed: "text-red-700",
};

export default async function RunsPage() {
  let runs: Run[] = [];
  let models: Model[] = [];
  let error: string | null = null;

  try {
    [runs, models] = await Promise.all([api.runs(), api.models()]);
  } catch {
    error = `Could not reach Rigor API at ${API_BASE}. Is the backend running?`;
  }

  const modelById = Object.fromEntries(models.map((m) => [m.id, m]));
  const sorted = [...runs].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="text-xl font-medium text-gray-900">Rigor</h1>
        <p className="text-sm text-gray-500 mt-1">LLM evaluation and regression platform</p>
      </div>

      {error ? (
        <p className="text-red-600 text-sm">{error}</p>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="pb-2 font-medium">Model</th>
              <th className="pb-2 font-medium">Provider</th>
              <th className="pb-2 font-medium">Status</th>
              <th className="pb-2 font-medium">Created</th>
              <th className="pb-2 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((run) => {
              const model = modelById[run.model_id];
              return (
                <tr key={run.id} className="border-b border-gray-100 hover:bg-white">
                  <td className="py-2 pr-4 font-mono text-xs text-gray-700">
                    {model?.name ?? run.model_id.slice(0, 8)}
                  </td>
                  <td className="py-2 pr-4 text-gray-500">{model?.provider ?? "—"}</td>
                  <td className={`py-2 pr-4 ${STATUS_COLORS[run.status] ?? "text-gray-700"}`}>
                    {run.status}
                  </td>
                  <td className="py-2 pr-4 text-gray-500">{formatDate(run.created_at)}</td>
                  <td className="py-2">
                    <Link href={`/runs/${run.id}`} className="text-blue-600 hover:underline">
                      Detail →
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
