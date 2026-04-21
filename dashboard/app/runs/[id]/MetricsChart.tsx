"use client";

import { MetricCI } from "@/lib/api";
import {
  BarChart,
  Bar,
  ErrorBar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

type Props = { metrics: Record<string, MetricCI> };

export default function MetricsChart({ metrics }: Props) {
  const data = Object.entries(metrics).map(([name, ci]) => ({
    name,
    mean: ci.mean,
    errorY: [ci.mean - ci.ci_low, ci.ci_high - ci.mean] as [number, number],
  }));

  return (
    <ResponsiveContainer width="100%" height={120 + data.length * 40}>
      <BarChart
        layout="vertical"
        data={data}
        margin={{ top: 4, right: 40, left: 80, bottom: 4 }}
      >
        <CartesianGrid horizontal={false} strokeDasharray="3 3" />
        <XAxis type="number" domain={[0, 1]} tickCount={6} tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={80} />
        <Tooltip
          formatter={(v) => (typeof v === "number" ? v.toFixed(3) : v)}
          labelFormatter={(l) => `Metric: ${l}`}
        />
        <Bar dataKey="mean" fill="#3b82f6" barSize={18}>
          {data.map((_, i) => (
            <Cell key={i} />
          ))}
          <ErrorBar dataKey="errorY" width={4} strokeWidth={2} stroke="#1d4ed8" direction="x" />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
