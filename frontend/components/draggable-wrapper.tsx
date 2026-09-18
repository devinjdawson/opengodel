"use client";

import React, { useState, useRef, useCallback, useEffect, ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";
import { Maximize2, Minimize2, X } from "lucide-react";

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
}

type ResizeHandle = "n" | "s" | "e" | "w" | "ne" | "nw" | "se" | "sw" | null;

const MIN_WIDTH = 280;
const MIN_HEIGHT = 150;

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
}: DraggableWrapperProps) {
  const [position, setPosition] = useState(defaultPosition);
  const [size, setSize] = useState(defaultSize);
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState<ResizeHandle>(null);
  const [isMaximized, setIsMaximized] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const dragOffset = useRef({ x: 0, y: 0 });
  const resizeStart = useRef({ x: 0, y: 0, width: 0, height: 0, posX: 0, posY: 0 });

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (e.button !== 0 || isMaximized) return;
      e.preventDefault();
      e.stopPropagation();

      onFocus?.();

      if (cardRef.current) {
        const rect = cardRef.current.getBoundingClientRect();
        dragOffset.current = {
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        };
        setIsDragging(true);
      }
    },
    [isMaximized, onFocus]
  );

  const handleResizeMouseDown = useCallback(
    (e: React.MouseEvent, handle: ResizeHandle) => {
      if (e.button !== 0 || isMaximized) return;
      e.preventDefault();
      e.stopPropagation();

      if (cardRef.current) {
        const rect = cardRef.current.getBoundingClientRect();
        resizeStart.current = {
          x: e.clientX,
          y: e.clientY,
          width: rect.width,
          height: rect.height,
          posX: position.x,
          posY: position.y,
        };
        setIsResizing(handle);
      }
    },
    [isMaximized, position]
  );

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        const newX = e.clientX - dragOffset.current.x;
        const newY = e.clientY - dragOffset.current.y;
        const newPos = { x: Math.max(0, newX), y: Math.max(0, newY) };
        setPosition(newPos);
        onPositionChange?.(newPos);
      } else if (isResizing && resizeStart.current) {
        const deltaX = e.clientX - resizeStart.current.x;
        const deltaY = e.clientY - resizeStart.current.y;
        let newWidth = resizeStart.current.width;
        let newHeight = resizeStart.current.height;
        let newX = resizeStart.current.posX;
        let newY = resizeStart.current.posY;

        switch (isResizing) {
          case "e":
            newWidth = Math.max(MIN_WIDTH, resizeStart.current.width + deltaX);
            break;
          case "w":
            newWidth = Math.max(MIN_WIDTH, resizeStart.current.width - deltaX);
            newX = resizeStart.current.posX + (resizeStart.current.width - newWidth);
            break;
          case "s":
            newHeight = Math.max(MIN_HEIGHT, resizeStart.current.height + deltaY);
            break;
          case "n":
            newHeight = Math.max(MIN_HEIGHT, resizeStart.current.height - deltaY);
            newY = resizeStart.current.posY + (resizeStart.current.height - newHeight);
            break;
          case "se":
            newWidth = Math.max(MIN_WIDTH, resizeStart.current.width + deltaX);
            newHeight = Math.max(MIN_HEIGHT, resizeStart.current.height + deltaY);
            break;
          case "sw":
            newWidth = Math.max(MIN_WIDTH, resizeStart.current.width - deltaX);
            newHeight = Math.max(MIN_HEIGHT, resizeStart.current.height + deltaY);
            newX = resizeStart.current.posX + (resizeStart.current.width - newWidth);
            break;
          case "ne":
            newWidth = Math.max(MIN_WIDTH, resizeStart.current.width + deltaX);
            newHeight = Math.max(MIN_HEIGHT, resizeStart.current.height - deltaY);
            newY = resizeStart.current.posY + (resizeStart.current.height - newHeight);
            break;
          case "nw":
            newWidth = Math.max(MIN_WIDTH, resizeStart.current.width - deltaX);
            newHeight = Math.max(MIN_HEIGHT, resizeStart.current.height - deltaY);
            newX = resizeStart.current.posX + (resizeStart.current.width - newWidth);
            newY = resizeStart.current.posY + (resizeStart.current.height - newHeight);
            break;
        }

        const newSize = { width: newWidth, height: newHeight };
        const newPos = { x: newX, y: newY };
        setSize(newSize);
        setPosition(newPos);
        onSizeChange?.(newSize);
        onPositionChange?.(newPos);
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      setIsResizing(null);
    };

    if (isDragging || isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      return () => {
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [isDragging, isResizing, onPositionChange, onSizeChange]);

  const toggleMaximize = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      setIsMaximized(!isMaximized);
    },
    [isMaximized]
  );

  const resizeHandles: { handle: ResizeHandle; className: string }[] = [
    { handle: "n", className: "absolute top-0 left-4 right-4 h-2 cursor-n-resize" },
    { handle: "s", className: "absolute bottom-0 left-4 right-4 h-2 cursor-s-resize" },
    { handle: "e", className: "absolute top-4 right-0 bottom-4 w-2 cursor-e-resize" },
    { handle: "w", className: "absolute top-4 left-0 bottom-4 w-2 cursor-w-resize" },
    { handle: "se", className: "absolute bottom-0 right-0 h-3 w-3 cursor-se-resize" },
    { handle: "sw", className: "absolute bottom-0 left-0 h-3 w-3 cursor-sw-resize" },
    { handle: "ne", className: "absolute top-0 right-0 h-3 w-3 cursor-ne-resize" },
    { handle: "nw", className: "absolute top-0 left-0 h-3 w-3 cursor-nw-resize" },
  ];

  return (
    <div
      ref={cardRef}
      style={{
        position: "fixed",
        left: isMaximized ? 0 : position.x,
        top: isMaximized ? 0 : position.y,
        width: isMaximized ? "100vw" : size.width,
        height: isMaximized ? "100vh" : size.height,
        zIndex,
      }}
      className={cn("select-none", isDragging && "cursor-grabbing")}
      onMouseDown={() => onFocus?.()}
    >
      <Card className="h-full w-full overflow-hidden border-2 border-gray-700 bg-gray-900 shadow-xl">
        <CardHeader
          className="flex flex-row items-center justify-between space-x-2 border-b border-gray-700 bg-gray-800 px-3 py-2 cursor-grab active:cursor-grabbing"
          onMouseDown={handleMouseDown}
        >
          <CardTitle className="flex-1 truncate text-sm font-medium text-gray-200">
            {title}
          </CardTitle>
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-gray-400 hover:bg-gray-700 hover:text-gray-200"
              onClick={toggleMaximize}
            >
              {isMaximized ? <Minimize2 className="h-3 w-3" /> : <Maximize2 className="h-3 w-3" />}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="relative h-[calc(100%-2.5rem)] overflow-auto p-0">
          {children}
          {!isMaximized &&
            resizeHandles.map(({ handle, className }) => (
              <div
                key={handle}
                className={className}
                onMouseDown={(e) => handleResizeMouseDown(e, handle)}
              />
            ))}
        </CardContent>
      </Card>
    </div>
  );
}

export default DraggableWrapper;
