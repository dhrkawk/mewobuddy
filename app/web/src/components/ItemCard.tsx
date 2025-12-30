import { Item } from "../types";

interface Props {
  item: Item;
}

export function ItemCard({ item }: Props) {
  const isLocked = item.status === "locked";
  const isEquipped = item.equipped && !isLocked;

  return (
    <div className="card overflow-hidden border border-slate-100">
      <div className="relative bg-slate-50 p-4">
        <div className="bg-white rounded-2xl p-4 flex items-center justify-center min-h-[220px]">
          <img src={item.image} alt={item.name} className="max-h-[200px] object-contain" />
        </div>
        {isLocked ? (
          <div className="absolute inset-0 bg-white/60 flex items-center justify-center text-2xl">
            🔒
          </div>
        ) : null}
        {isEquipped ? (
          <div className="absolute top-4 right-4 bg-emerald-500 text-white text-xs px-3 py-1 rounded-full">
            장착 중
          </div>
        ) : null}
      </div>
      <div className="p-4 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="text-lg font-semibold text-slate-900">{item.name}</div>
          {isLocked && item.price ? (
            <div className="text-brand font-semibold text-sm">{item.price}</div>
          ) : null}
        </div>
        {isLocked ? (
          <button className="w-full rounded-lg py-2 text-sm font-semibold border border-slate-200 text-slate-700">
            구매하기
          </button>
        ) : (
          <button
            className={`w-full rounded-lg py-2 text-sm font-semibold ${
              isEquipped ? "bg-emerald-200 text-emerald-700" : "border border-slate-200 text-slate-700"
            }`}
            disabled={isEquipped}
          >
            {isEquipped ? "장착됨" : "장착"}
          </button>
        )}
      </div>
    </div>
  );
}
