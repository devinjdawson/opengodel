"use client";

import React, { ReactNode, useCallback, useEffect, useRef, useState } from "react";
import { animate, motion, useMotionValue } from "motion/react";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";
import { Maximize2, Minimize2 } from "lucide-react";

interface DraggableWrapperProps {
  children: ReactNode;
  title?: string;
  className?: string;
  defaultPosition?: { x: number; y: number };
  defaultSize?: { width: number; height: number };
  onPositionChange?: (position: { x: number; y: number }) => void;
  onSizeChange?: (size: { width: number; height: number }) => void;
  onFocus?: () => void;
  zIndex?: number;
  containerBounds?: { width: number; height: number };
}

type ResizeHandle = "n" | "s" | "e" | "w" | "ne" | "nw" | "se" | "sw";

const MIN_WIDTH = 280;
const MIN_HEIGHT = 150;
const SNAP_THRESHOLD = 7;
const SPRING = { type: "spring", stiffness: 420, damping: 34 } as const;
const GUIDE_Z = 9999;

interface Guides {
  v: number | null;
  h: number | null;
}

export function DraggableWrapper({
  children,
  title,
  className,
  defaultPosition = { x: 100, y: 100 },
  defaultSize = { width: 400, height: 300 },
  onPositionChange,
  onSizeChange,
  onFocus,
  zIndex = 10,
  containerBounds,
}: DraggableWrapperProps) {
  const x = useMotionValue(defaultPosition.x);
  const y = useMotionValue(defaultPosition.y);
  const w = useMotionValue(defaultSize.width);
  const h = useMotionValue(defaultSize.height);

  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ px: number; py: number; x: number; y: number } | null>(null);
  const [resizeState, setResizeState] = useState<{
    handle: ResizeHandle;
    pointerX: number;
    pointerY: number;
    x: number;
    y: number;
    w: number;
    h: number;
  } | null>(null);
  const [isMaximized, setIsMaximized] = useState(false);
  const [guides, setGuides] = useState<Guides>({ v: null, h: null });

  const guidesRef = useRef<Guides>({ v: null, h: null });
  const restoreRect = useRef({ x: defaultPosition.x, y: defaultPosition.y, w: defaultSize.width, h: defaultSize.height });

  const boundsW = containerBounds?.width || 0;
  const boundsH = containerBounds?.height || 0;
  const isResizing = resizeState !== null;
  const busy = isDragging || isResizing;

  const updateGuides = (v: number | null, hLine: number | null) => {
    const g = guidesRef.current;
    if (g.v !== v || g.h !== hLine) {
      guidesRef.current = { v, h: hLine };
      setGuides({ v, h: hLine });
    }
  };

  useEffect(() => {
    if (!boundsW || !boundsH) return;
    const cw = Math.min(w.get(), boundsW);
    const ch = Math.min(h.get(), boundsH);
    if (cw !== w.get() || ch !== h.get()) {
      w.set(cw);
      h.set(ch);
    }
    const maxX = Math.max(0, boundsW - w.get());
    const maxY = Math.max(0, boundsH - h.get());
    if (x.get() < 0) x.set(0);
    if (y.get() < 0) y.set(0);
    if (x.get() > maxX) x.set(maxX);
    if (y.get() > maxY) y.set(maxY);
  }, [boundsW, boundsH, x, y, w, h]);

  const beginDrag = (e: React.PointerEvent) => {
    if (isMaximized || e.button !== 0) return;
    onFocus?.();
    (e.target as Element).setPointerCapture(e.pointerId);
    setDragStart({ px: e.clientX, py: e.clientY, x: x.get(), y: y.get() });
    setIsDragging(true);
  };

  const moveDrag = (e: React.PointerEvent) => {
    if (!dragStart || !boundsW || !boundsH) return;
    const cw = w.get();
    const ch = h.get();
    let nx = dragStart.x + (e.clientX - dragStart.px);
    let ny = dragStart.y + (e.clientY - dragStart.py);

    nx = Math.max(0, Math.min(nx, boundsW - cw));
    ny = Math.max(0, Math.min(ny, boundsH - ch));

    let snapV: number | null = null;
    let snapH: number | null = null;
    for (const t of [0, (boundsW - cw) / 2, boundsW - cw]) {
      if (Math.abs(nx - t) < SNAP_THRESHOLD) {
        nx = t;
        snapV = t === 0 ? 0 : t === boundsW - cw ? boundsW : boundsW / 2;
        break;
      }
    }
    for (const t of [0, (boundsH - ch) / 2, boundsH - ch]) {
      if (Math.abs(ny - t) < SNAP_THRESHOLD) {
        ny = t;
        snapH = t === 0 ? 0 : t === boundsH - ch ? boundsH : boundsH / 2;
        break;
      }
    }

    x.set(nx);
    y.set(ny);
    updateGuides(snapV, snapH);
  };

  const endDrag = () => {
    if (!dragStart) return;
    setDragStart(null);
    setIsDragging(false);
    updateGuides(null, null);
    onPositionChange?.({ x: Math.round(x.get()), y: Math.round(y.get()) });
  };

  const beginResize = (e: React.PointerEvent, handle: ResizeHandle) => {
    if (e.button !== 0 || isMaximized) return;
    e.preventDefault();
    e.stopPropagation();
    onFocus?.();
    (e.target as Element).setPointerCapture(e.pointerId);
    setResizeState({
      handle,
      pointerX: e.clientX,
      pointerY: e.clientY,
      x: x.get(),
      y: y.get(),
      w: w.get(),
      h: h.get(),
    });
  };

  const moveResize = (e: React.PointerEvent) => {
    if (!resizeState) return;
    const { handle, pointerX, pointerY } = resizeState;
    const s = resizeState;
    const dx = e.clientX - pointerX;
    const dy = e.clientY - pointerY;
    let nx = s.x;
    let ny = s.y;
    let nw = s.w;
    let nh = s.h;

    if (handle.includes("e")) nw = s.w + dx;
    if (handle.includes("s")) nh = s.h + dy;
    if (handle.includes("w")) {
      nw = s.w - dx;
      nx = s.x + dx;
    }
    if (handle.includes("n")) {
      nh = s.h - dy;
      ny = s.y + dy;
    }

    if (nw < MIN_WIDTH) {
      if (handle.includes("w")) nx = s.x + (s.w - MIN_WIDTH);
      nw = MIN_WIDTH;
    }
    if (nh < MIN_HEIGHT) {
      if (handle.includes("n")) ny = s.y + (s.h - MIN_HEIGHT);
      nh = MIN_HEIGHT;
    }

    if (boundsW && boundsH) {
      nx = Math.max(0, nx);
      ny = Math.max(0, ny);
      if (nx + nw > boundsW) nw = boundsW - nx;
      if (ny + nh > boundsH) nh = boundsH - ny;
    }

    x.set(nx);
    y.set(ny);
    w.set(nw);
    h.set(nh);
  };

  const endResize = () => {
    if (!resizeState) return;
    setResizeState(null);
    onSizeChange?.({ width: Math.round(w.get()), height: Math.round(h.get()) });
    onPositionChange?.({ x: Math.round(x.get()), y: Math.round(y.get()) });
  };

  const toggleMaximize = useCallback(() => {
    onFocus?.();
    if (!boundsW || !boundsH) return;
    if (isMaximized) {
      const r = restoreRect.current;
      animate(x, r.x, SPRING);
      animate(y, r.y, SPRING);
      animate(w, r.w, SPRING);
      animate(h, r.h, SPRING);
      setIsMaximized(false);
    } else {
      restoreRect.current = { x: x.get(), y: y.get(), w: w.get(), h: h.get() };
      animate(x, 0, SPRING);
      animate(y, 0, SPRING);
      animate(w, boundsW, SPRING);
      animate(h, boundsH, SPRING);
      setIsMaximized(true);
    }
  }, [isMaximized, boundsW, boundsH, onFocus, x, y, w, h]);

  const resizeHandles: { handle: ResizeHandle; className: string }[] = [
    { handle: "n", className: "top-0 left-3 right-3 h-1.5 cursor-n-resize" },
    { handle: "s", className: "bottom-0 left-3 right-3 h-1.5 cursor-s-resize" },
    { handle: "e", className: "top-3 right-0 bottom-3 w-1.5 cursor-e-resize" },
    { handle: "w", className: "top-3 left-0 bottom-3 w-1.5 cursor-w-resize" },
    { handle: "ne", className: "top-0 right-0 h-4 w-4 cursor-ne-resize" },
    { handle: "nw", className: "top-0 left-0 h-4 w-4 cursor-nw-resize" },
    { handle: "se", className: "bottom-0 right-0 h-4 w-4 cursor-se-resize" },
    { handle: "sw", className: "bottom-0 left-0 h-4 w-4 cursor-sw-resize" },
  ];

  return (
    <>
      {(guides.v !== null || guides.h !== null) && (
        <div className="pointer-events-none absolute inset-0" style={{ zIndex: GUIDE_Z }}>
          {guides.v !== null && (
            <div
              className="absolute top-0 bottom-0 w-px bg-sky-400/80 shadow-[0_0_6px_rgba(56,189,248,0.9)]"
              style={{ left: guides.v }}
            />
          )}
          {guides.h !== null && (
            <div
              className="absolute left-0 right-0 h-px bg-sky-400/80 shadow-[0_0_6px_rgba(56,189,248,0.9)]"
              style={{ top: guides.h }}
            />
          )}
        </div>
      )}

      <motion.div
        className={cn("group absolute left-0 top-0", className)}
        style={{ x, y, width: w, height: h, zIndex, willChange: "transform" }}
        onPointerDownCapture={() => onFocus?.()}
      >
        <motion.div
          animate={{ scale: isDragging ? 1.01 : 1 }}
          transition={{ scale: SPRING }}
          className={cn(
            "relative h-full w-full overflow-hidden rounded-lg border bg-[#0b0f14]/95 backdrop-blur-sm transition-shadow duration-150",
            busy
              ? "border-white/20 shadow-[0_24px_60px_-12px_rgba(0,0,0,0.85)]"
              : "border-white/10 shadow-[0_12px_32px_-12px_rgba(0,0,0,0.7)]"
          )}
        >
          <div
            className={cn(
              "flex h-8 items-center gap-2 border-b bg-gradient-to-b from-white/[0.07] to-white/[0.02] px-2",
              busy ? "cursor-grabbing" : "cursor-grab"
            )}
            style={{ touchAction: "none" }}
            onPointerDown={beginDrag}
            onPointerMove={moveDrag}
            onPointerUp={endDrag}
            onPointerCancel={endDrag}
            onDoubleClick={toggleMaximize}
          >
            <div className="flex items-center gap-1 pl-0.5 opacity-40">
              <span className="size-1 rounded-full bg-zinc-400" />
              <span className="size-1 rounded-full bg-zinc-400" />
              <span className="size-1 rounded-full bg-zinc-400" />
            </div>
            <span className="flex-1 truncate text-xs font-medium text-zinc-200">
              {title}
            </span>
            <Button
              variant="ghost"
              size="icon"
              className="size-6 text-zinc-400 hover:bg-white/10 hover:text-zinc-100"
              onClick={(e) => {
                e.stopPropagation();
                toggleMaximize();
              }}
              onPointerDown={(e) => e.stopPropagation()}
              aria-label={isMaximized ? "Restore" : "Maximize"}
            >
              {isMaximized ? <Minimize2 className="size-3.5" /> : <Maximize2 className="size-3.5" />}
            </Button>
          </div>

          <div className="absolute inset-x-0 bottom-0 overflow-auto" style={{ top: 32 }}>
            <div className={cn("h-full w-full", busy && "pointer-events-none")}>
              {children}
            </div>
          </div>

          {!isMaximized &&
            resizeHandles.map(({ handle, className }) => (
              <div
                key={handle}
                className={cn("absolute z-10", className)}
                style={{ touchAction: "none" }}
                onPointerDown={(e) => beginResize(e, handle)}
                onPointerMove={(e) => resizeState?.handle === handle && moveResize(e)}
                onPointerUp={endResize}
                onPointerCancel={endResize}
              />
            ))}

          {!isMaximized && (
            <div className="pointer-events-none absolute bottom-1 right-1 z-10 opacity-0 transition-opacity group-hover:opacity-40">
              <svg width="10" height="10" viewBox="0 0 10 10" className="text-zinc-300">
                <path d="M9 1v8H1M9 5v4H5" stroke="currentColor" fill="none" strokeWidth="1" />
              </svg>
            </div>
          )}
        </motion.div>
      </motion.div>
    </>
  );
}

export default DraggableWrapper;
