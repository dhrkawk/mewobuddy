import { RadioItem } from "../types";

interface Props {
  item: RadioItem;
}

export function RadioItemCard({ item }: Props) {
  return (
    <div className="card px-4 py-3 flex items-center gap-3">
      <div className="h-10 w-10 rounded-full bg-brand/15 text-brand flex items-center justify-center">
        ▶
      </div>
      <div className="flex-1">
        <div className="text-slate-900 font-medium">{item.title}</div>
        <div className="text-slate-500 text-sm">{item.date}</div>
      </div>
      <div className="text-slate-500 text-sm">{item.length}</div>
    </div>
  );
}
