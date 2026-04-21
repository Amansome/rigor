const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export type Run = {
  id: string;
  dataset_id: string;
  model_id: string;
  prompt_id: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
};

export type MetricCI = {
  mean: number;
  ci_low: number;
  ci_high: number;
  n_samples: number;
  confidence: number;
  n_iterations: number;
};

export type RunSummary = {
  run_id: string;
  status: string;
  n_results: number;
  n_errors: number;
  metrics: Record<string, MetricCI>;
};

export type PairedTestResult = {
  test_name: string;
  n_pairs: number;
  mean_difference: number;
  p_value: number;
  significant_at_0_05: boolean;
};

export type CompareResult = {
  run_a: string;
  run_b: string;
  metric: string;
  n_pairs: number;
  mean_a: number;
  mean_b: number;
  mean_difference: number;
  tests: {
    paired_permutation: PairedTestResult;
    wilcoxon_signed_rank: PairedTestResult;
  };
};

export type Model = {
  id: string;
  name: string;
  provider: string;
  created_at: string;
};

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${path} returned ${res.status}`);
  return res.json();
}

export const api = {
  runs: () => apiFetch<Run[]>("/runs"),
  run: (id: string) => apiFetch<Run>(`/runs/${id}`),
  summary: (id: string) => apiFetch<RunSummary>(`/runs/${id}/summary`),
  compare: (a: string, b: string, metric = "pass_at_1") =>
    apiFetch<CompareResult>(`/runs/${a}/compare/${b}?metric=${metric}`),
  models: () => apiFetch<Model[]>("/models"),
};
