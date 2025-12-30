import { useMemo, useState } from "react";
import { Item } from "../types";
import { Section } from "../components/Section";
import { ItemCard } from "../components/ItemCard";

interface Props {
  owned: Item[];
  shop: Item[];
}

type InventoryTab = "owned" | "shop";
type CategoryTab = "skin" | "motion";

export function InventoryPage({ owned, shop }: Props) {
  const [inventoryTab, setInventoryTab] = useState<InventoryTab>("owned");
  const [categoryTab, setCategoryTab] = useState<CategoryTab>("skin");

  const visibleItems = useMemo(() => {
    const source = inventoryTab === "owned" ? owned : shop;
    return source.filter((item) => item.category === categoryTab);
  }, [inventoryTab, categoryTab, owned, shop]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button
          className={`px-6 py-2 rounded-full text-sm font-semibold border ${
            inventoryTab === "owned"
              ? "bg-brand text-white border-brand"
              : "bg-white text-slate-500 border-slate-200"
          }`}
          onClick={() => setInventoryTab("owned")}
        >
          내 보관함
        </button>
        <button
          className={`px-6 py-2 rounded-full text-sm font-semibold border ${
            inventoryTab === "shop"
              ? "bg-brand text-white border-brand"
              : "bg-white text-slate-500 border-slate-200"
          }`}
          onClick={() => setInventoryTab("shop")}
        >
          상점
        </button>
      </div>

      <div className="flex items-center gap-3">
        <button
          className={`px-6 py-2 rounded-full text-sm font-semibold border ${
            categoryTab === "skin"
              ? "bg-brand text-white border-brand"
              : "bg-white text-slate-500 border-slate-200"
          }`}
          onClick={() => setCategoryTab("skin")}
        >
          스킨
        </button>
        <button
          className={`px-6 py-2 rounded-full text-sm font-semibold border ${
            categoryTab === "motion"
              ? "bg-brand text-white border-brand"
              : "bg-white text-slate-500 border-slate-200"
          }`}
          onClick={() => setCategoryTab("motion")}
        >
          모션
        </button>
      </div>

      <Section icon="" title={inventoryTab === "owned" ? "내 보관함" : "상점"}>
        <div className="grid grid-cols-2 gap-6">
          {visibleItems.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      </Section>
    </div>
  );
}
