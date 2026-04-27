type Props = { mean: number; ci_low: number; ci_high: number };

export default function CIBar({ mean, ci_low, ci_high }: Props) {
  const lowPct  = `${(ci_low  * 100).toFixed(3)}%`;
  const widPct  = `${((ci_high - ci_low) * 100).toFixed(3)}%`;
  const meanPct = `${(mean * 100).toFixed(3)}%`;

  return (
    <div className="relative h-6 bg-surface rounded-sm overflow-hidden flex-1 min-w-0">
      {/* CI interval fill */}
      <div
        className="absolute inset-y-0 bg-accent/20"
        style={{ left: lowPct, width: widPct }}
      />
      {/* Mean tick */}
      <div
        className="absolute inset-y-1 w-px bg-accent"
        style={{ left: meanPct }}
      />
    </div>
  );
}
