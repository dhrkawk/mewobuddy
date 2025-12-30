import { GoalMetric } from "../types";

interface Props {
  metric: GoalMetric;
}

export function GoalBar({ metric }: Props) {
  const progress = Math.min(metric.current / metric.target, 1);
  const pct = Math.round(progress * 100);

  return (
    <div className="card p-4">
      <div className="text-slate-900 font-semibold mb-2">{metric.label}</div>
      <div className="w-full h-4 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-full bg-emerald-500" style={{ width: `${pct}%` }} />
      </div>
      <div className="text-brand mt-2 font-medium">
        {metric.current.toLocaleString()} / {metric.target.toLocaleString()} {metric.unit}
      </div>
    </div>
  );
}
