interface Props {
  onLogout?: () => void;
}

export function SettingsPage({ onLogout }: Props) {
  return (
    <div className="space-y-4 max-w-md">
      <div className="card p-5 flex flex-col gap-3">
        <div className="text-lg font-semibold text-slate-900">계정</div>
        <button
          className="bg-brand text-white rounded-lg px-4 py-2 text-sm font-semibold"
          onClick={onLogout}
        >
          로그아웃
        </button>
        <div className="text-slate-500 text-sm">버전 0.1.0</div>
      </div>
    </div>
  );
}
