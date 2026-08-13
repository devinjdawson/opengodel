"use client";

import { useState, useEffect, useRef } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, RefreshCw, Search, ChevronDown, ChevronUp, BarChart3, LineChart, PieChart, Table, Settings, Grid, LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";

interface WidgetConfig {
  id: string;
  name: string;
  description: string;
  category: string;
  type: "chart" | "table";
  endpoint: string;
  gridData: { w: number; h: number };
  source: string;
  data: any;
  params: WidgetParam[];
}

interface WidgetParam {
  paramName: string;
  value: string | number | boolean;
  label: string;
  show: boolean;
  description: string;
  type: "text" | "number" | "boolean" | "date";
  options?: { label: string; value: string }[];
}

interface Template {
  name: string;
  tabs: Record<string, { id: string; name: string; layout: LayoutItem[] }>;
}

interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  state?: any;
}

interface WidgetState {
  params: Record<string, string | number | boolean>;
  data: any;
  loading: boolean;
  error: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DashboardPage() {
  const [widgets, setWidgets] = useState<Record<string, WidgetConfig>>({});
  const [templates, setTemplates] = useState<Template[]>([]);
  const [activeTemplate, setActiveTemplate] = useState<string>("Equity Analysis");
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [widgetStates, setWidgetStates] = useState<Record<string, WidgetState>>({});
  const [loading, setLoading] = useState(true);
  const [globalParams, setGlobalParams] = useState<Record<string, string>>({
    symbol: "AAPL",
    start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
    end_date: new Date().toISOString().split("T")[0],
  });

  // Load widgets and templates on mount
  useEffect(() => {
    loadWidgetsAndTemplates();
  }, []);

  const loadWidgetsAndTemplates = async () => {
    try {
      const [widgetsRes, templatesRes] = await Promise.all([
        fetch(`${API_BASE}/widgets.json`),
        fetch(`${API_BASE}/templates.json`),
      ]);
      
      const widgetsData = await widgetsRes.json();
      const templatesData = await templatesRes.json();
      
      // Convert widgets array to object keyed by endpoint
      const widgetsObj: Record<string, WidgetConfig> = {};
      for (const widget of widgetsData) {
        widgetsObj[widget.endpoint] = widget;
      }
      
      setWidgets(widgetsObj);
      setTemplates(templatesData);
      
      // Initialize widget states
      const initialStates: Record<string, WidgetState> = {};
      for (const widget of widgetsData) {
        const params: Record<string, string | number | boolean> = {};
        for (const param of widget.params) {
          params[param.paramName] = param.value;
        }
        // Override with global params if matching
        for (const [key, value] of Object.entries(globalParams)) {
          if (params.hasOwnProperty(key)) {
            params[key] = value;
          }
        }
        initialStates[widget.endpoint] = {
          params,
          data: null,
          loading: false,
          error: null,
        };
      }
      setWidgetStates(initialStates);
      setLoading(false);
    } catch (error) {
      console.error("Failed to load widgets:", error);
      setLoading(false);
    }
  };

  const fetchWidgetData = async (endpoint: string) => {
    const widget = widgets[endpoint];
    if (!widget) return;

    const state = widgetStates[endpoint];
    setWidgetStates(prev => ({
      ...prev,
      [endpoint]: { ...state, loading: true, error: null },
    }));

    try {
      // Build query params
      const params = new URLSearchParams();
      for (const [key, value] of Object.entries(state.params)) {
        params.append(key, String(value));
      }

      const response = await fetch(`${API_BASE}/api/v1/widgets/${widget.category.toLowerCase()}/${endpoint}?${params}`);
      const data = await response.json();

      setWidgetStates(prev => ({
        ...prev,
        [endpoint]: { ...state, loading: false, data, error: null },
      }));
    } catch (error) {
      setWidgetStates(prev => ({
        ...prev,
        [endpoint]: { ...state, loading: false, error: String(error) },
      }));
    }
  };

  const updateWidgetParam = (endpoint: string, paramName: string, value: string | number | boolean) => {
    setWidgetStates(prev => ({
      ...prev,
      [endpoint]: {
        ...prev[endpoint],
        params: { ...prev[endpoint].params, [paramName]: value },
      },
    }));
  };

  const handleGlobalParamChange = (key: string, value: string) => {
    setGlobalParams(prev => ({ ...prev, [key]: value }));
    // Update all widgets that have this param
    setWidgetStates(prev => {
      const next = { ...prev };
      for (const [endpoint, state] of Object.entries(next)) {
        if (state.params.hasOwnProperty(key)) {
          next[endpoint] = {
            ...state,
            params: { ...state.params, [key]: value },
          };
        }
      }
      return next;
    });
  };

  const refreshWidget = (endpoint: string) => {
    fetchWidgetData(endpoint);
  };

  const refreshAllWidgets = () => {
    const template = templates.find(t => t.name === activeTemplate);
    if (!template) return;
    const tab = template.tabs[activeTab];
    if (!tab) return;
    
    for (const item of tab.layout) {
      fetchWidgetData(item.i);
    }
  };

  const getTemplate = () => templates.find(t => t.name === activeTemplate);
  const getCurrentTab = () => getTemplate()?.tabs[activeTab];
  const getTabLayout = () => getCurrentTab()?.layout || [];

  const renderWidget = (widget: WidgetConfig, state: WidgetState) => {
    if (state.loading) {
      return (
        <div className="flex items-center justify-center h-[300px]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      );
    }

    if (state.error) {
      return (
        <div className="flex items-center justify-center h-[300px] text-destructive">
          <div className="text-center">
            <p>Error loading widget</p>
            <p className="text-sm">{state.error}</p>
            <Button size="sm" onClick={() => refreshWidget(widget.endpoint)} className="mt-2">
              <RefreshCw className="h-4 w-4 mr-1" />
              Retry
            </Button>
          </div>
        </div>
      );
    }

    if (widget.type === "chart" && state.data) {
      return <PlotlyChart data={state.data} />;
    }

    if (widget.type === "table" && state.data) {
      return <DataTable data={state.data} columns={widget.data?.table?.columnsDefs || []} />;
    }

    return (
      <div className="flex items-center justify-center h-[300px] text-muted-foreground">
        No data available
      </div>
    );
  };

  const renderParamControls = (widget: WidgetConfig, state: WidgetState) => {
    const visibleParams = widget.params.filter(p => p.show);
    if (visibleParams.length === 0) return null;

    return (
      <div className="flex flex-wrap gap-2 p-3 bg-muted/50 rounded-lg border">
        {visibleParams.map(param => {
          const value = state.params[param.paramName];
          switch (param.type) {
            case "boolean":
              return (
                <label key={param.paramName} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={value === true}
                    onChange={e => updateWidgetParam(widget.endpoint, param.paramName, e.target.checked)}
                    className="rounded border-input"
                  />
                  <span>{param.label}</span>
                </label>
              );
            case "number":
              return (
                <div className="flex items-center gap-1">
                  <label className="text-sm text-muted-foreground">{param.label}</label>
                  <input
                    type="number"
                    value={String(value)}
                    onChange={e => updateWidgetParam(widget.endpoint, param.paramName, Number(e.target.value))}
                    className="w-24 px-2 py-1 text-sm border rounded bg-background"
                  />
                </div>
              );
            case "date":
              return (
                <div className="flex items-center gap-1">
                  <label className="text-sm text-muted-foreground">{param.label}</label>
                  <input
                    type="date"
                    value={String(value)}
                    onChange={e => updateWidgetParam(widget.endpoint, param.paramName, e.target.value)}
                    className="w-40 px-2 py-1 text-sm border rounded bg-background"
                  />
                </div>
              );
            case "text":
            default:
              if (param.options && param.options.length > 0) {
                return (
                  <div className="flex items-center gap-1">
                    <label className="text-sm text-muted-foreground">{param.label}</label>
                    <Select
                      value={String(value)}
                      onValueChange={v => v !== null && updateWidgetParam(widget.endpoint, param.paramName, v)}
                    >
                      <SelectTrigger className="w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {param.options.map(opt => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                );
              }
              return (
                <div className="flex items-center gap-1">
                  <label className="text-sm text-muted-foreground">{param.label}</label>
                  <input
                    type="text"
                    value={String(value)}
                    onChange={e => updateWidgetParam(widget.endpoint, param.paramName, e.target.value)}
                    className="w-40 px-2 py-1 text-sm border rounded bg-background"
                    placeholder={param.description}
                  />
                </div>
              );
          }
        })}
        <Button
          size="sm"
          variant="outline"
          onClick={() => refreshWidget(widget.endpoint)}
          disabled={state.loading}
        >
          <RefreshCw className="h-4 w-4 mr-1" />
          Refresh
        </Button>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

  const template = getTemplate();
  const currentTab = getCurrentTab();
  const layout = getTabLayout();

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <div className="border-b p-4 bg-card">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold">OpenBB Financial Dashboard</h1>
            
            {/* Template Selector */}
            <Select value={activeTemplate} onValueChange={v => v !== null && setActiveTemplate(v)}>
              <SelectTrigger className="w-52">
                <SelectValue placeholder="Select Dashboard" />
              </SelectTrigger>
              <SelectContent>
                {templates.map(t => (
                  <SelectItem key={t.name} value={t.name}>
                    {t.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Tab Selector */}
            {template && (
              <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
                <TabsList className="grid w-full">
                  {Object.values(template.tabs).map(tab => (
                    <TabsTrigger key={tab.id} value={tab.id}>
                      {tab.name}
                    </TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            )}
          </div>

          {/* Global Parameters */}
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-muted-foreground">Symbol:</label>
              <Input
                value={globalParams.symbol}
                onChange={e => handleGlobalParamChange("symbol", e.target.value.toUpperCase())}
                placeholder="AAPL"
                className="w-32"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm text-muted-foreground">Start:</label>
              <Input
                type="date"
                value={globalParams.start_date}
                onChange={e => handleGlobalParamChange("start_date", e.target.value)}
                className="w-40"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm text-muted-foreground">End:</label>
              <Input
                type="date"
                value={globalParams.end_date}
                onChange={e => handleGlobalParamChange("end_date", e.target.value)}
                className="w-40"
              />
            </div>
            <Button
              onClick={refreshAllWidgets}
              disabled={layout.some(item => widgetStates[item.i]?.loading)}
            >
              <RefreshCw className={cn("h-4 w-4 mr-1", layout.some(item => widgetStates[item.i]?.loading) && "animate-spin")} />
              Refresh All
            </Button>
          </div>
        </div>
      </div>

      {/* Dashboard Grid */}
      <div className="flex-1 overflow-auto p-4">
        {layout.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p>No widgets in this tab. Select a different template or tab.</p>
          </div>
        ) : (
          <div className="grid gap-4" style={{ gridTemplateColumns: "repeat(12, 1fr)" }}>
            {layout.map(item => {
              const widget = widgets[item.i];
              const state = widget ? widgetStates[item.i] : null;
              
              if (!widget || !state) {
                return (
                  <div
                    key={item.i}
                    className="border border-dashed border-destructive p-4"
                    style={{
                      gridColumn: `span ${item.w / 3.33}`,
                      gridRow: `span ${item.h / 5}`,
                    }}
                  >
                    Widget not found: {item.i}
                  </div>
                );
              }

              return (
                <Card
                  key={item.i}
                  className="flex flex-col overflow-hidden"
                  style={{
                    gridColumn: `span ${item.w / 3.33}`,
                    gridRow: `span ${item.h / 5}`,
                    minHeight: `${item.h * 20}px`,
                  }}
                >
                  <CardHeader className="flex flex-row items-center justify-between p-3 pb-2">
                    <CardTitle className="text-lg">{widget.name}</CardTitle>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-muted-foreground">{widget.category}</span>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => refreshWidget(widget.endpoint)}
                        disabled={state.loading}
                        className="h-7 w-7"
                      >
                        <RefreshCw className={cn("h-4 w-4", state.loading && "animate-spin")} />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col p-3 pt-0">
                    {renderParamControls(widget, state)}
                    <div className="flex-1 min-h-0">
                      {renderWidget(widget, state)}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

// Simple Plotly chart renderer
function PlotlyChart({ data }: { data: any }) {
  const ref = useRef<HTMLDivElement | null>(null);
  
  useEffect(() => {
    if (!ref.current || !data) return;
    
    // Dynamic import of plotly.js-dist
    import("plotly.js-dist").then(Plotly => {
      Plotly.newPlot(ref.current!, data.data || data, data.layout || {}, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ["lasso2d", "select2d"],
      });
    });
  }, [data]);

  return <div ref={ref} style={{ width: "100%", height: "100%", minHeight: "300px" }} />;
}

// Data table component
function DataTable({ data, columns }: { data: any[]; columns: any[] }) {
  if (!data || data.length === 0) {
    return <div className="text-center text-muted-foreground py-8">No data</div>;
  }

  const cols = columns.length > 0 ? columns : Object.keys(data[0]).map(key => ({ field: key, headerName: key }));

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b">
            {cols.map(col => (
              <th key={col.field} className="text-left p-2 font-medium text-muted-foreground">
                {col.headerName || col.field}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr key={rowIdx} className="border-b hover:bg-muted/50">
              {cols.map(col => {
                const value = row[col.field];
                let displayValue = value;
                
                if (col.renderFn === "link" && value) {
                  return (
                    <td key={col.field} className="p-2">
                      <a href={value} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                        Link
                      </a>
                    </td>
                  );
                }
                
                if (col.renderFn === "percent" && typeof value === "number") {
                  displayValue = `${(value * 100).toFixed(2)}%`;
                }
                
                if (col.renderFn === "greenRed" && typeof value === "number") {
                  return (
                    <td key={col.field} className={`p-2 ${value >= 0 ? "text-green-500" : "text-red-500"}`}>
                      {value >= 0 ? "+" : ""}{value.toFixed(2)}
                    </td>
                  );
                }
                
                return (
                  <td key={col.field} className="p-2">
                    {displayValue ?? "—"}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}