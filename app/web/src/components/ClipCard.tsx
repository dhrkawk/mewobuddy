import { Clip } from "../types";

interface Props {
  clip: Clip;
}

export function ClipCard({ clip }: Props) {
  return (
    <div className="card overflow-hidden border border-slate-100">
      <div className="relative">
        <img src={clip.thumbnail} alt={clip.title} className="w-full h-64 object-cover" />
        <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded-md">
          {clip.duration}
        </div>
      </div>
      <div className="p-4">
        <div className="text-slate-900 font-semibold">{clip.title}</div>
        <div className="text-slate-500 text-sm">{clip.views}</div>
      </div>
    </div>
  );
}
