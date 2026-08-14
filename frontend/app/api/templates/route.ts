import { NextResponse } from "next/server";
import { readFileSync } from "fs";
import { join } from "path";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2000);
    const res = await fetch("http://localhost:8001/templates.json", {
      signal: controller.signal,
      cache: "no-store",
    });
    clearTimeout(timeout);
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch {
    // backend unavailable, fall back to static file
  }

  try {
    const staticPath = join(process.cwd(), "public", "templates.json");
    const data = JSON.parse(readFileSync(staticPath, "utf-8"));
    return NextResponse.json(data);
  } catch {
    return NextResponse.json([], { status: 200 });
  }
}
