"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const API_HINT = (process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1")
  .replace(/^https?:\/\//, "")
  .replace(/\/.*$/, "");

function NavLink({ href, label, active }: { href: string; label: string; active: boolean }) {
  return (
    <Link
      href={href}
      className={`relative h-12 flex items-center text-[14px] transition-colors duration-150 ${
        active ? "text-ink font-medium" : "text-muted hover:text-ink"
      }`}
    >
      {label}
      {active && (
        <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent" />
      )}
    </Link>
  );
}

export default function Nav() {
  const path = usePathname();

  return (
    <nav className="bg-card border-b border-rim">
      <div className="max-w-4xl mx-auto px-6 h-12 flex items-center gap-6">
        <span className="text-[15px] font-medium text-ink mr-2">Rigor</span>
        <NavLink href="/" label="Runs" active={path === "/" || path.startsWith("/runs")} />
        <NavLink href="/compare" label="Compare" active={path === "/compare"} />
        <span className="ml-auto font-mono text-[11px] text-faint">{API_HINT}</span>
      </div>
    </nav>
  );
}
