import { useState } from "react";
import { TopNav } from "./components/TopNav";
import { HomePage } from "./pages/HomePage";
import { InventoryPage } from "./pages/InventoryPage";
import { SettingsPage } from "./pages/SettingsPage";
import { notices } from "./mock/notices";
import { hotClips } from "./mock/hot_clips";
import { radioItems } from "./mock/radio";
import { goalMetrics } from "./mock/goals";
import { ownedItems, shopItems } from "./mock/items";
import { Page } from "./types";

function App() {
  const [page, setPage] = useState<Page>("home");

  return (
    <div className="bg-soft min-h-screen text-slate-900">
      <div className="max-w-[1280px] mx-auto px-6 pb-10">
        <TopNav current={page} onChange={setPage} />
        {page === "home" && (
          <HomePage notices={notices} radioItems={radioItems} goalMetrics={goalMetrics} hotClips={hotClips} />
        )}
        {page === "inventory" && <InventoryPage owned={ownedItems} shop={shopItems} />}
        {page === "settings" && <SettingsPage onLogout={() => console.log("logout clicked")} />}
      </div>
    </div>
  );
}

export default App;
