import { Stream } from "../types";

interface Props {
  stream: Stream;
}

export function StreamItem({ stream }: Props) {
  return (
    <div className="card px-4 py-3 flex items-center gap-3">
      <div className="h-10 w-10 rounded-full bg-brand/15 text-brand flex items-center justify-center">▶</div>
      <div className="flex flex-col">
        <div className="text-slate-900 font-medium">{stream.title}</div>
        <div className="text-slate-500 text-sm">{stream.date} · {stream.length}</div>
      </div>
    </div>
  );
}
