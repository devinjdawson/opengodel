# Docked Resizable Panel Workspace (replace floating windows)

## Goal
Swap the free-floating `DraggableWrapper` window canvas for a docked split-pane workspace built on shadcn `Resizable` (`react-resizable-panels` v4): panels tile the dashboard, resize via keyboard-accessible handles between them, and add/remove from the widget drawer rebalances the tree.

## 1. Install
- `npx shadcn@latest add resizable` in `frontend/` → creates `components/ui/resizable.tsx` (base style). If the generated file has the bogus `import { cn } from "cn"` (seen with drawer), fix to `@/lib/utils`.
- This adds `react-resizable-panels` to `package.json`.
- v4 API: `<ResizablePanelGroup orientation="horizontal"|"vertical">`, `<ResizablePanel defaultSize="50%" minSize="15%">`, `<ResizableHandle withHandle />`; sizes captured via `onLayoutChange`.

## 2. New layout model — `frontend/lib/panel-layout.ts`
```ts
type LayoutNode =
  | { kind: "panel"; endpoint: string }
  | { kind: "group"; orientation: "horizontal" | "vertical"; children: LayoutNode[] };
```
Pure functions (unit-testable):
- `gridToTree(items)` — recursive guillotine slicing of a tab's `x/y/w/h` grid into a tree: find a full vertical/horizontal cut line that separates the item set, recurse; if unsliceable/overlapping (e.g. Equity "overview" has the heatmap overlapping the candlestick), drop the covering duplicate and split rows by y-bands. Deterministic so template loads look stable.
- `addWidget(tree, endpoint)` — split the largest leaf (orientation alternating by depth) into a group with the old leaf + new panel.
- `removeWidget(tree, endpoint)` — delete leaf; collapse single-child groups; merge nested same-orientation groups.
- `countPanels(tree)`.

## 3. State & persistence in `frontend/app/dashboard/page.tsx`
- Replace grid/window state with a `Record<templateName, Record<tabId, LayoutNode>>` in state, seeded on template load from:
  1. `localStorage["og-panel-layout:{template}:{tab}"]` (tree + sizes), else
  2. `gridToTree(template tab layout)`, else empty tree.
- Panel sizes: map per group id captured from each group's `onLayoutChange`; persisted with the tree (debounced). Re-hydrate `defaultSize` from the map so user resizes survive structural changes as well as the tree shape allows.
- `addWidgetToDashboard` / `removeWidgetFromDashboard` mutate the tree for the active template+tab.

## 4. Rendering
- Recursive `renderNode(node)`:
  - `panel` → `ResizablePanel minSize="15%"` → card chrome (header: widget title + refresh + remove "X"; body: existing `renderParamControls` + `renderWidget`).
  - `group` → `ResizablePanelGroup orientation=...` with `ResizableHandle withHandle` between children, `onLayoutChange` wired to the sizes map.
- Root fills `main` (`h-full w-full`, keep `bg-gray-950`); remove `canvasRef`/`canvasSize` ResizeObserver + `containerBounds` wiring.
- Keep the empty-state view when `countPanels === 0` (Browse Widgets → opens drawer, unchanged).
- Keep the PlotlyChart `ResizeObserver` fix from the last iteration — it is now the mechanism that reflows charts when panels are resized.

## 5. Cleanup
- Delete `frontend/components/draggable-wrapper.tsx` and its import.
- Remove window management: `windowZIndices`, `topZIndex`, `bringWindowToFront`, maximize/drag/snap-guide concepts, now-unused icon imports.

## 6. Verification
- `npx eslint` + `npm run typecheck`: no new errors in touched files (pre-existing `any`/ai-elements errors expected).
- Browser (`localhost:3001/dashboard`):
  1. Equity Analysis tab tiles load from the template (no overlap).
  2. Drag a handle to resize; chart content reflows; arrow keys work on a focused handle.
  3. Add a widget from the drawer → splits in; remove → collapses; empty state shows at 0 panels.
  4. Reload → layout + sizes restore from localStorage.
  5. Switch tabs/templates → each keeps its own tree.

## Out of scope (follow-ups)
- Per-panel "pop out" to a floating window (hybrid model).
- Saving layout server-side per user/template.
