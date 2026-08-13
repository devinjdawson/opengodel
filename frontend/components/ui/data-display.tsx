"use client";

import { cn } from "@/lib/utils";

export function PanelSection({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <section className={cn("space-y-2", className)}>
      {children}
    </section>
  );
}

export function PanelHeader({ title, badge, className }: { title: string; badge?: string | React.ReactNode; className?: string }) {
  return (
    <div className={cn("flex items-center justify-between gap-2", className)}>
      <h2 className="text-lg font-semibold">{title}</h2>
      {badge && (
        <span className="badge px-2 py-0.5 text-xs">
          {badge}
        </span>
      )}
    </div>
  );
}

export function CardNotice({ children, tone = "info", className }: { children: React.ReactNode; tone?: "info" | "danger" | "warning" | "success"; className?: string }) {
  const tones = {
    info: "border-[#3a5ea8] bg-[#1e2d4a]/50",
    danger: "border-[#ff6b6b]/50 bg-[#4a1e1e]/50",
    warning: "border-[#ffcc00]/50 bg-[#4a3e1e]/50",
    success: "border-[#5ec4ff]/50 bg-[#1e4a3e]/50",
  };
  return (
    <div className={cn("card p-3 text-sm", tones[tone], className)}>
      {children}
    </div>
  );
}

export function InlineNotice({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("card p-3 text-sm text-[#9aaccc]", className)}>
      {children}
    </div>
  );
}

export function EmptyTableRow({ colSpan, message }: { colSpan: number; message: string }) {
  return (
    <tr>
      <td colSpan={colSpan} className="px-3 py-6 text-center text-[#9aaccc]">
        {message}
      </td>
    </tr>
  );
}