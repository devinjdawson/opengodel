"use client";

import Link from "next/link";

interface TickerBoardLinkProps {
  symbol: string;
  className?: string;
  children?: React.ReactNode;
}

export function TickerBoardLink({ symbol, className, children }: TickerBoardLinkProps) {
  return (
    <Link href={`/ticker/${symbol}`} className={className}>
      {children ?? symbol}
    </Link>
  );
}