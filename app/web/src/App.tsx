import { useEffect, useState } from "react";
import { TopNav } from "./components/TopNav";
import { HomePage } from "./pages/HomePage";
import { InventoryPage } from "./pages/InventoryPage";
import { SettingsPage } from "./pages/SettingsPage";
import { notices as mockNotices } from "./mock/notices";
import { hotClips } from "./mock/hot_clips";
import { radioItems } from "./mock/radio";
import { goalMetrics } from "./mock/goals";
import { ownedItems, shopItems } from "./mock/items";
import { Page, Notice } from "./types";

function App() {
  const [page, setPage] = useState<Page>("home");
  const [notices, setNotices] = useState<Notice[]>(mockNotices);
  const [noticeLoading, setNoticeLoading] = useState(false);
  const [noticeError, setNoticeError] = useState<string | null>(null);

  const [apiBase] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    const val = params.get("api_base") || "";
    return val.replace(/\/+$/, "");
  });
  const [token] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("token") || "";
  });

  useEffect(() => {
    if (!apiBase || !token) {
      return;
    }
    let cancelled = false;
    setNoticeLoading(true);
    setNoticeError(null);
    fetch(`${apiBase}/notices`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (resp) => {
        if (!resp.ok) {
          const text = await resp.text();
          throw new Error(text || resp.statusText);
        }
        return resp.json();
      })
      .then((data) => {
        if (!cancelled) {
          const normalized = Array.isArray(data)
            ? data.map((notice: Record<string, unknown>) => {
                const createdRaw =
                  (notice.created_at as string | undefined) ??
                  (notice.createdAt as string | undefined) ??
                  "";
                const createdAt =
                  typeof createdRaw === "string" && createdRaw.includes("T")
                    ? createdRaw.split("T")[0]
                    : String(createdRaw || "");
                return {
                  id: String((notice.id as string | undefined) ?? ""),
                  title: String((notice.title as string | undefined) ?? ""),
                  content: String((notice.content as string | undefined) ?? ""),
                  createdAt,
                };
              })
            : [];
          setNotices(normalized);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setNoticeError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setNoticeLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [apiBase, token]);

  return (
    <div className="bg-soft min-h-screen text-slate-900">
      <div className="max-w-[1280px] mx-auto px-6 pb-10">
        <TopNav current={page} onChange={setPage} />
        {page === "home" && (
          <HomePage
            notices={notices}
            noticeLoading={noticeLoading}
            noticeError={noticeError}
            radioItems={radioItems}
            goalMetrics={goalMetrics}
            hotClips={hotClips}
          />
        )}
        {page === "inventory" && <InventoryPage owned={ownedItems} shop={shopItems} />}
        {page === "settings" && <SettingsPage onLogout={() => console.log("logout clicked")} />}
      </div>
    </div>
  );
}

export default App;
