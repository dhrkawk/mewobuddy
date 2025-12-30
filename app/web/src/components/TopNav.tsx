import { Page } from "../types";

interface Props {
  current: Page;
  onChange: (page: Page) => void;
}

const navItems: { key: Page; label: string }[] = [
  { key: "home", label: "홈" },
  { key: "inventory", label: "보관함" },
  { key: "settings", label: "설정" },
];

export function TopNav({ current, onChange }: Props) {
  return (
    <div className="flex items-center justify-between py-4 border-b border-slate-100">
      <div className="flex items-center gap-4">
        <img src="assets/logo.svg" alt="MeowBuddy" className="h-12 w-12" />
        <div className="leading-tight">
          <div className="text-2xl font-semibold">MeowBuddy</div>
          <div className="text-sm text-slate-500">데스크탑 위젯 매니저</div>
        </div>
      </div>
      <div className="flex items-center gap-2 bg-slate-50 px-2 py-1 rounded-full">
        {navItems.map((item) => (
          <button
            key={item.key}
            onClick={() => onChange(item.key)}
            className={`px-5 py-2 rounded-full text-sm font-medium transition ${
              current === item.key
                ? "bg-brand/20 text-brand"
                : "text-slate-500 hover:bg-slate-100"
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
