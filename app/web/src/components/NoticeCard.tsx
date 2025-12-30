import { Notice } from "../types";

interface Props {
  notice: Notice;
}

export function NoticeCard({ notice }: Props) {
  return (
    <div className="card p-4 flex flex-col gap-2 border border-slate-100">
      <div className="flex items-start justify-between gap-3">
        <div className="text-base font-semibold text-slate-900">{notice.title}</div>
        <div className="text-sm text-slate-400 whitespace-nowrap">{notice.createdAt}</div>
      </div>
      <div className="text-slate-600 text-sm leading-relaxed">{notice.content}</div>
    </div>
  );
}
