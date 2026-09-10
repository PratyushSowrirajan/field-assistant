import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { to: "/", label: "Home", end: true },
  { to: "/overview", label: "Overview" },
  { to: "/fields", label: "Fields" },
  { to: "/live", label: "Live Rover" },
  { to: "/insights", label: "Insights" },
  { to: "/alerts", label: "Alerts" },
  // Isolated, removable feature — see src/features/leaf-check/README.md
  { to: "/leaf-check", label: "Leaf Check" },
  { to: "/assistant", label: "Assistant" },
];

export default function Layout() {
  const { farmer, logout } = useAuth();

  return (
    <div className="min-h-screen bg-cream">
      <header className="sticky top-0 z-30 border-b border-sand bg-cream/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-forest text-cream">
              <LeafIcon className="h-5 w-5" />
            </div>
            <span className="text-lg font-semibold text-forest">Smart Farming Assistant</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-ink/70 sm:inline">{farmer?.name}</span>
            <button
              onClick={logout}
              className="rounded-md border border-sand px-3 py-1.5 text-sm text-ink/70 hover:bg-sand"
            >
              Sign out
            </button>
          </div>
        </div>
        <nav className="mx-auto flex max-w-6xl gap-1 overflow-x-auto px-4 pb-2 sm:px-6">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `whitespace-nowrap rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                  isActive ? "bg-forest text-cream" : "text-ink/70 hover:bg-sand"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
        <Outlet />
      </main>
    </div>
  );
}

function LeafIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M5 19c8 0 14-6 14-14 0 0-12-1-14 8-1 4 0 6 0 6Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M5 19c0-4 2-8 6-10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
