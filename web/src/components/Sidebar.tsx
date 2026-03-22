"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Dashboard", icon: "◆" },
  { href: "/create", label: "Create", icon: "+" },
  { href: "/posts", label: "Posts", icon: "◻" },
  { href: "/ideas", label: "Ideas", icon: "✦" },
  { href: "/influencers", label: "Influencers", icon: "◉" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 min-h-screen border-r flex flex-col py-6 px-4"
      style={{ borderColor: "var(--border)", background: "var(--card)" }}>
      <div className="mb-8 px-2">
        <h1 className="text-lg font-bold" style={{ color: "var(--accent)" }}>
          Content Engine
        </h1>
        <p className="text-xs mt-1" style={{ color: "var(--muted)" }}>
          LinkedIn Pipeline
        </p>
      </div>

      <nav className="flex flex-col gap-1">
        {NAV.map(({ href, label, icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                active
                  ? "font-semibold"
                  : "hover:bg-white/5"
              }`}
              style={active ? { background: "var(--accent)", color: "var(--background)" } : {}}
            >
              <span className="text-base">{icon}</span>
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
