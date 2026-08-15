"use client";

import { useEffect, useRef, useState, ReactNode } from "react";
import { createSwapy } from "swapy";
import { cn } from "@/lib/utils";

interface SwapyLayoutProps {
  children: ReactNode;
  className?: string;
  onLayoutChange?: (layout: Record<string, string>) => void;
  initialLayout?: Record<string, string>;
  enabled?: boolean;
}

export function SwapyContainer({
  children,
  className,
  onLayoutChange,
  initialLayout,
  enabled = true,
}: SwapyLayoutProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const swapyRef = useRef<ReturnType<typeof createSwapy> | null>(null);

  // Initialize swapy once
  useEffect(() => {
    if (!containerRef.current) return;

    swapyRef.current = createSwapy(containerRef.current, {
      animation: "dynamic",
    });

    swapyRef.current.onSwap((event) => {
      if (onLayoutChange) {
        // swapy v1.0.5 uses newSlotItemMap.asObject
        onLayoutChange(event.newSlotItemMap.asObject as Record<string, string>);
      }
    });

    return () => {
      swapyRef.current?.destroy();
      swapyRef.current = null;
    };
  }, []);

  // Toggle enabled state
  useEffect(() => {
    swapyRef.current?.enable(enabled);
  }, [enabled]);

  return (
    <div ref={containerRef} className={cn("grid gap-4", className)}>
      {children}
    </div>
  );
}

interface SwapySlotProps {
  id: string;
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

export function SwapySlot({ id, children, className, style }: SwapySlotProps) {
  return (
    <div data-swapy-slot={id} className={className} style={style}>
      {children}
    </div>
  );
}

interface SwapyItemProps {
  id: string;
  children: ReactNode;
  className?: string;
}

export function SwapyItem({ id, children, className }: SwapyItemProps) {
  return (
    <div data-swapy-item={id} className={className}>
      {children}
    </div>
  );
}

interface SwapyHandleProps {
  className?: string;
}

export function SwapyHandle({ className }: SwapyHandleProps) {
  return (
    <div
      data-swapy-handle
      className={cn(
        "cursor-move absolute top-2 left-2 z-10 p-1 rounded bg-background/80 hover:bg-background border border-border/50 opacity-0 group-hover:opacity-100 transition-opacity",
        className
      )}
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle cx="9" cy="5" r="1" />
        <circle cx="9" cy="12" r="1" />
        <circle cx="9" cy="19" r="1" />
        <circle cx="15" cy="5" r="1" />
        <circle cx="15" cy="12" r="1" />
        <circle cx="15" cy="19" r="1" />
      </svg>
    </div>
  );
}

// Hook for persisting layout to localStorage
export function useSwapyLayout(storageKey: string) {
  const [layout, setLayout] = useState<Record<string, string>>({});

  useEffect(() => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      try {
        setLayout(JSON.parse(saved));
      } catch {
        // Invalid JSON, use empty layout
      }
    }
  }, [storageKey]);

  const saveLayout = (newLayout: Record<string, string>) => {
    setLayout(newLayout);
    localStorage.setItem(storageKey, JSON.stringify(newLayout));
  };

  return { layout, saveLayout };
}
