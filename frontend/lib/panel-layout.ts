/**
 * Docked-panel layout tree for the dashboard workspace.
 *
 * The workspace is a binary-ish tree of nested split groups:
 *   group("vertical")
 *   ├── group("horizontal")  -> row 1: two panels side by side
 *   ├── group("horizontal")  -> row 2
 *   └── panel("financials")  -> full-width row
 *
 * `gridToTree` converts a template tab's react-grid-style items into a clean,
 * deterministic tiling (rows of up to 2 panels, ordered by y then x). The
 * source x/y/w/h values overlap in some templates, so only the ordering is
 * honored; users resize/persist afterwards.
 *
 * Group `sizes` maps child panel id -> percentage (0..100), captured from
 * react-resizable-panels `onLayoutChanged` and persisted in localStorage.
 */

export type LayoutNode =
  | { kind: "panel"; endpoint: string }
  | {
      kind: "group";
      orientation: "horizontal" | "vertical";
      sizes?: Record<string, number>;
      children: LayoutNode[];
    };

export type PanelGroupNode = Extract<LayoutNode, { kind: "group" }>;

export interface GridItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

const flip = (o: "horizontal" | "vertical"): "horizontal" | "vertical" =>
  o === "horizontal" ? "vertical" : "horizontal";

export function gridToTree(items: GridItem[]): LayoutNode | null {
  if (items.length === 0) return null;
  const sorted = [...items].sort((a, b) => a.y - b.y || a.x - b.x);
  if (sorted.length === 1) return { kind: "panel", endpoint: sorted[0].i };

  const rows: GridItem[][] = [];
  for (let i = 0; i < sorted.length; i += 2) rows.push(sorted.slice(i, i + 2));

  const children: LayoutNode[] = rows.map(row =>
    row.length === 1
      ? { kind: "panel" as const, endpoint: row[0].i }
      : {
          kind: "group" as const,
          orientation: "horizontal" as const,
          children: row.map(it => ({ kind: "panel" as const, endpoint: it.i })),
        }
  );
  return { kind: "group", orientation: "vertical", children };
}

/** Append a new panel by splitting the last (bottom-right) leaf. */
export function addWidget(tree: LayoutNode | null, endpoint: string): LayoutNode {
  const leaf: LayoutNode = { kind: "panel", endpoint };
  if (!tree) return leaf;
  if (tree.kind === "panel") {
    return { kind: "group", orientation: "horizontal", children: [tree, leaf] };
  }
  const children = [...tree.children];
  const last = children[children.length - 1];
  children[children.length - 1] =
    last.kind === "group"
      ? addWidget(last, endpoint)
      : { kind: "group", orientation: flip(tree.orientation), children: [last, leaf] };
  return { ...tree, children };
}

/** Remove a leaf, collapsing single-child groups and merging same-orientation nesting. */
export function removeWidget(tree: LayoutNode | null, endpoint: string): LayoutNode | null {
  if (!tree) return null;
  if (tree.kind === "panel") return tree.endpoint === endpoint ? null : tree;

  const children = tree.children
    .map(c => removeWidget(c, endpoint))
    .filter((c): c is LayoutNode => c !== null);

  if (children.length === 0) return null;
  if (children.length === 1) {
    const only = children[0];
    if (only.kind === "group" && only.orientation === tree.orientation) {
      return { ...tree, children: only.children };
    }
    return only;
  }
  return { ...tree, children };
}

/** Immutably set the captured child sizes for the group at `path` (index path from root). */
export function setGroupSizes(
  tree: LayoutNode,
  path: number[],
  sizes: Record<string, number>
): LayoutNode {
  if (tree.kind !== "group") return tree;
  if (path.length === 0) return { ...tree, sizes };
  const [head, ...rest] = path;
  const children = tree.children.map((c, i) => (i === head ? setGroupSizes(c, rest, sizes) : c));
  return { ...tree, children };
}

export function countPanels(tree: LayoutNode | null): number {
  if (!tree) return 0;
  if (tree.kind === "panel") return 1;
  return tree.children.reduce((n, c) => n + countPanels(c), 0);
}

/** All panel endpoints contained in the tree. */
export function listEndpoints(tree: LayoutNode | null): string[] {
  if (!tree) return [];
  if (tree.kind === "panel") return [tree.endpoint];
  return tree.children.flatMap(listEndpoints);
}
