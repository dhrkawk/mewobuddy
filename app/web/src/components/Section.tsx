interface Props {
  icon?: string;
  title: string;
  children?: React.ReactNode;
}

export function Section({ icon, title, children }: Props) {
  return (
    <div className="w-full">
      <div className="flex items-center gap-2 text-lg font-semibold mb-3 text-slate-800">
        {icon ? <span className="text-base">{icon}</span> : null}
        <span>{title}</span>
      </div>
      {children}
    </div>
  );
}
