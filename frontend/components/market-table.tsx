"use client";

import { formatPrice, formatPercent, formatInteger, pctColorClass } from "@/lib/format";
import { TickerBoardLink } from "@/components/ticker-board-link";
import { EmptyTableRow } from "@/components/ui/data-display";

interface MarketRow {
  symbol: string;
  name?: string;
  price?: number;
  percent_change?: number | null;
  volume?: number;
  market_cap?: number | null;
  market_cap_bucket?: "Micro" | "Small" | "Mid" | "Large" | "Mega" | null;
}

interface MarketTableProps {
  title: string;
  rows: MarketRow[];
}

export function MarketTable({ title, rows }: MarketTableProps) {
  return (
    <div className="card flex flex-col">
      <div className="card-header p-3">
        <h3 className="font-semibold">{title}</h3>
      </div>
      <div className="table-wrap flex-1 overflow-auto">
        <table className="table w-full">
          <thead>
            <tr className="text-xs text-[#9aaccc] uppercase tracking-wider">
              <th className="px-3 py-2 text-left">Symbol</th>
              <th className="px-3 py-2 text-left">Name</th>
              <th className="px-3 py-2 text-right">Price</th>
              <th className="px-3 py-2 text-right">Change %</th>
              <th className="px-3 py-2 text-right">Volume</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <EmptyTableRow colSpan={5} message="No data available." />
            ) : (
              rows.map((row) => (
                <tr key={row.symbol} className="border-t border-[#2a3a5a] hover:bg-[#1a2a4a]">
                  <td className="px-3 py-2">
                    <TickerBoardLink className="font-semibold text-[#5ec4ff]" symbol={row.symbol}>
                      {row.symbol}
                    </TickerBoardLink>
                  </td>
                  <td className="px-3 py-2 text-sm text-[#9aaccc] max-w-[180px] truncate">
                    {row.name || "—"}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-sm">
                    {formatPrice(row.price)}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-sm">
                    <span className={pctColorClass(row.percent_change)}>
                      {formatPercent(row.percent_change)}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right text-sm text-[#9aaccc] font-mono">
                    {formatInteger(row.volume)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}