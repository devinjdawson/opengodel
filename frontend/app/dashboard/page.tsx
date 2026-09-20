"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, RefreshCw, Search, BarChart3, LineChart, PieChart, Table, Settings, Grid, LayoutDashboard, MessageSquare, X, Plus, FolderOpen, History, Bot, User, Send, Mic, Paperclip, TrendingUp, Heart, GripVertical, Pencil, PanelLeft, Bitcoin } from "lucide-react";
import { motion, LayoutGroup } from "motion/react";
import { cn } from "@/lib/utils";
import { DraggableWrapper } from "@/components/draggable-wrapper";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { useIsMobile } from "@/hooks/use-mobile";

interface WidgetConfig {
  id: string;
  name: string;
  description: string;
  category: string;
  type: "chart" | "table" | "heatmap";
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

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  widgets?: string[];
}

const CATEGORIES = [
  { id: "equity", name: "Equity", icon: BarChart3 },
  { id: "market", name: "Market", icon: TrendingUp },
  { id: "macro", name: "Macro", icon: LineChart },
  { id: "news", name: "News", icon: MessageSquare },
  { id: "options", name: "Options", icon: PieChart },
  { id: "portfolio", name: "Portfolio", icon: Table },
  { id: "sentiment", name: "Sentiment", icon: Heart },
  { id: "crypto", name: "Crypto", icon: Bitcoin },
  { id: "og", name: "OG Terminal", icon: Settings },
];

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
  
  // Sidebar states
  const [drawerOpen, setDrawerOpen] = useState(false);
  const isMobile = useIsMobile();
  const [rightSidebarOpen, setRightSidebarOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string>("equity");
  const [widgetSearch, setWidgetSearch] = useState("");
  
  // Chat states
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "assistant",
      content: "Welcome to OG Terminal! I'm your AI financial assistant. Ask me about stocks, market data, technical analysis, or create custom widgets.",
      timestamp: new Date(),
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLDivElement>(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  // Window management
  const [topZIndex, setTopZIndex] = useState(100);
  const [windowZIndices, setWindowZIndices] = useState<Record<string, number>>({});
  const [widgetOrder, setWidgetOrder] = useState<Record<string, string>>({});

  // Default data provider
  const [dataProvider, setDataProvider] = useState<string>("yfinance");

  useEffect(() => {
    const saved = localStorage.getItem("defaultDataProvider");
    if (saved) {
      setDataProvider(saved);
    }
  }, []);

  const handleProviderChange = async (provider: string | null) => {
    if (!provider) return;
    setDataProvider(provider);
    localStorage.setItem("defaultDataProvider", provider);
    // Update backend setting
    try {
      await fetch(`/api/v1/widgets/og/settings/provider?provider=${provider}`, { method: "PUT" });
    } catch (e) {
      console.error("Failed to update provider:", e);
    }
  };

  // Load widget order from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(`dashboard-order-${activeTemplate}-${activeTab}`);
    if (saved) {
      try {
        setWidgetOrder(JSON.parse(saved));
      } catch {
        // Invalid JSON, use default order
      }
    }
  }, [activeTemplate, activeTab]);

  // Save widget order to localStorage
  const saveWidgetOrder = (order: Record<string, string>) => {
    setWidgetOrder(order);
    localStorage.setItem(`dashboard-order-${activeTemplate}-${activeTab}`, JSON.stringify(order));
  };

  const bringWindowToFront = (widgetId: string) => {
    const newZIndex = topZIndex + 1;
    setTopZIndex(newZIndex);
    setWindowZIndices(prev => ({ ...prev, [widgetId]: newZIndex }));
  };

  // Load widgets and templates on mount
  useEffect(() => {
    loadWidgetsAndTemplates();
  }, []);

  // Auto-fetch data for all widgets in the current tab
  useEffect(() => {
    if (loading) return;
    const template = getTemplate();
    if (!template) return;
    const tab = template.tabs[activeTab];
    if (!tab) return;

    for (const item of tab.layout) {
      if (widgetStates[item.i] && !widgetStates[item.i].data && !widgetStates[item.i].loading) {
        fetchWidgetData(item.i);
      }
    }
  }, [activeTemplate, activeTab, loading]);

  const categoryToPath = (cat: string): string => {
    const map: Record<string, string> = {
      "OG Terminal": "og",
      "og terminal": "og",
      Equity: "equity",
      equity: "equity",
      Macro: "macro",
      macro: "macro",
      News: "news",
      news: "news",
      Options: "options",
      options: "options",
      Portfolio: "portfolio",
      portfolio: "portfolio",
      Market: "market",
      market: "market",
      Sentiment: "sentiment",
      sentiment: "sentiment",
      Crypto: "crypto",
      crypto: "crypto",
    };
    return map[cat] || cat.toLowerCase().replace(/\s+/g, "-");
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  useEffect(() => {
    if (!canvasRef.current) return;
    const observer = new ResizeObserver(entries => {
      const rect = entries[0]?.contentRect;
      if (rect) setCanvasSize({ width: rect.width, height: rect.height });
    });
    observer.observe(canvasRef.current);
    return () => observer.disconnect();
  }, [loading]);

  // Auto-refresh heatmap at configured interval
  useEffect(() => {
    const template = getTemplate();
    const tab = getCurrentTab();
    if (!template || !tab) return;
    
    const heatmapItem = tab.layout.find(item => item.i === "market-heatmap");
    if (!heatmapItem) return;
    
    const state = widgetStates["market-heatmap"];
    if (!state) return;
    
    const refreshSec = Number(state.params?.refresh_interval || 0);
    if (!refreshSec || refreshSec <= 0) return;
    
    const interval = setInterval(() => {
      fetchWidgetData("market-heatmap");
    }, refreshSec * 1000);
    
    return () => clearInterval(interval);
  }, [activeTemplate, activeTab, widgetStates]);

  const loadWidgetsAndTemplates = async () => {
    try {
      const [widgetsRes, templatesRes] = await Promise.all([
        fetch('/api/widgets'),
        fetch('/api/templates'),
      ]);
      
      if (!widgetsRes.ok && !templatesRes.ok) {
        console.warn("Failed to fetch widgets/templates, using empty state");
      }
      
      let rawWidgets: unknown = null;
      let templatesData: unknown = null;
      
      if (widgetsRes.ok) rawWidgets = await widgetsRes.json();
      if (templatesRes.ok) templatesData = await templatesRes.json();
      
      let widgetsArray: unknown[];
      if (Array.isArray(rawWidgets)) {
        widgetsArray = rawWidgets;
      } else if (rawWidgets && typeof rawWidgets === "object") {
        widgetsArray = Object.values(rawWidgets);
      } else {
        widgetsArray = [];
      }
      
      const widgetsObj: Record<string, WidgetConfig> = {};
      for (const widget of widgetsArray) {
        const w = widget as WidgetConfig;
        if (w.endpoint) widgetsObj[w.endpoint] = w;
      }
      
      setWidgets(widgetsObj);
      setTemplates(Array.isArray(templatesData) ? templatesData : []);
      
      const initialStates: Record<string, WidgetState> = {};
      for (const widget of widgetsArray) {
        const w = widget as WidgetConfig;
        if (!w.endpoint) continue;
        const params: Record<string, string | number | boolean> = {};
        for (const param of w.params || []) {
          params[param.paramName] = param.value;
        }
        for (const [key, value] of Object.entries(globalParams)) {
          if (params.hasOwnProperty(key)) {
            params[key] = value;
          }
        }
        initialStates[w.endpoint] = {
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
      [endpoint]: { ...prev[endpoint], loading: true, error: null },
    }));

    try {
      const params = new URLSearchParams();
      for (const [key, value] of Object.entries(state?.params || {})) {
        params.append(key, String(value));
      }

      const categoryPath = categoryToPath(widget.category);
      const response = await fetch(`/api/v1/widgets/${categoryPath}/${endpoint}?${params}`);
      const data = await response.json();

      if (!response.ok) {
        const errorMsg = data?.error || data?.detail || `HTTP ${response.status}`;
        setWidgetStates(prev => ({
          ...prev,
          [endpoint]: { ...prev[endpoint], loading: false, data: null, error: errorMsg },
        }));
        return;
      }

      setWidgetStates(prev => ({
        ...prev,
        [endpoint]: { ...prev[endpoint], loading: false, data, error: null },
      }));
    } catch (error) {
      setWidgetStates(prev => ({
        ...prev,
        [endpoint]: { ...prev[endpoint], loading: false, error: String(error) },
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
    // Trigger data refresh with new params
    fetchWidgetData(endpoint);
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

  // Widget filtering
  const getFilteredWidgets = () => {
    return Object.values(widgets).filter(w => 
      w.category.toLowerCase() === activeCategory.toLowerCase() &&
      (w.name.toLowerCase().includes(widgetSearch.toLowerCase()) ||
       w.description.toLowerCase().includes(widgetSearch.toLowerCase()))
    );
  };

  // Chat functions
  const sendChatMessage = async () => {
    if (!chatInput.trim() || chatLoading) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: chatInput,
      timestamp: new Date(),
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    const query = chatInput;
    setChatInput("");
    setChatLoading(true);

    try {
      // Call the chat/agent endpoint
      const response = await fetch(`/api/ai/agent/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query, context: { symbol: globalParams.symbol } }),
      });
      
      const data = await response.json();
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response || data.message || "I couldn't process that request.",
        timestamp: new Date(),
        widgets: data.widgets || [],
      };
      
      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Error: ${String(error)}`,
        timestamp: new Date(),
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  const addWidgetToDashboard = (endpoint: string) => {
    const template = getTemplate();
    const tab = getCurrentTab();
    if (!template || !tab) return;
    
    const widget = widgets[endpoint];
    if (!widget) return;

    // Find next available position
    const maxY = Math.max(...tab.layout.map(l => l.y + l.h), 0);
    const newItem: LayoutItem = {
      i: endpoint,
      x: 0,
      y: maxY,
      w: widget.gridData.w,
      h: widget.gridData.h,
    };

    setTemplates(prev => prev.map(t => {
      if (t.name !== activeTemplate) return t;
      return {
        ...t,
        tabs: {
          ...t.tabs,
          [activeTab]: {
            ...t.tabs[activeTab],
            layout: [...t.tabs[activeTab].layout, newItem],
          },
        },
      };
    }));

    // Initialize widget state
    const params: Record<string, string | number | boolean> = {};
    for (const param of widget.params) {
      params[param.paramName] = param.value;
    }
    for (const [key, value] of Object.entries(globalParams)) {
      if (params.hasOwnProperty(key)) {
        params[key] = value;
      }
    }
    setWidgetStates(prev => ({
      ...prev,
      [endpoint]: { params, data: null, loading: false, error: null },
    }));

    // Auto-fetch data
    fetchWidgetData(endpoint);
  };

  const removeWidgetFromDashboard = (endpoint: string) => {
    const template = getTemplate();
    if (!template) return;

    setTemplates(prev => prev.map(t => {
      if (t.name !== activeTemplate) return t;
      return {
        ...t,
        tabs: Object.fromEntries(
          Object.entries(t.tabs).map(([tabId, tab]) => [
            tabId,
            {
              ...tab,
              layout: tab.layout.filter(item => item.i !== endpoint),
            },
          ])
        ),
      };
    }));
  };

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

    if (!state.data) {
      return (
        <div className="flex items-center justify-center h-[300px] text-muted-foreground">
          No data available
        </div>
      );
    }

    const responseType = state.data?.type;

    if (responseType === "error") {
      return (
        <div className="flex items-center justify-center h-[300px] text-destructive">
          <div className="text-center">
            <p>Error</p>
            <p className="text-sm">{state.data.error}</p>
            <Button size="sm" onClick={() => refreshWidget(widget.endpoint)} className="mt-2">
              <RefreshCw className="h-4 w-4 mr-1" />
              Retry
            </Button>
          </div>
        </div>
      );
    }

    if (widget.type === "chart" && state.data) {
      const chartData = state.data.data?.chart?.data || state.data.data?.chart || state.data;
      return <PlotlyChart data={chartData} />;
    }

    if (widget.type === "heatmap" && state.data) {
      const heatmapData = state.data.data?.length ? state.data : state.data.data?.chart?.data || state.data.data?.chart || state.data;
      return <StockHeatmap data={heatmapData} widgetParams={state.params} onParamChange={(param, value) => updateWidgetParam(widget.endpoint, param, value as string | number | boolean)} />;
    }

    if (widget.type === "table" && state.data) {
      const tableData = state.data.data?.table?.data || state.data.data || state.data;
      const columns = state.data.data?.table?.columnsDefs || widget.data?.table?.columnsDefs || [];
      return <DataTable data={tableData} columns={columns} />;
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
                <div key={param.paramName} className="flex items-center gap-1">
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
                <div key={param.paramName} className="flex items-center gap-1">
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
                  <div key={param.paramName} className="flex items-center gap-1">
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
                <div key={param.paramName} className="flex items-center gap-1">
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
  const filteredWidgets = getFilteredWidgets();
  const isWidgetOnDashboard = (endpoint: string) => layout.some(item => item.i === endpoint);

  return (
    <div className="flex h-dvh bg-background overflow-hidden">
      {/* Widget Library Drawer */}
      <Drawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        showSwipeHandle={isMobile}
        swipeDirection={isMobile ? "down" : "left"}
      >
        <DrawerContent className={cn("flex-col", !isMobile && "[--drawer-content-width:20rem]")}>
          <DrawerHeader className="border-b p-2">
            <div className="flex items-center justify-between w-full">
              <DrawerTitle>Widget Library</DrawerTitle>
              <DrawerClose
                render={
                  <Button variant="ghost" size="icon" className="size-8" aria-label="Close widget library" />
                }
              >
                <X className="size-4" />
              </DrawerClose>
            </div>
            <DrawerDescription className="sr-only">
              Browse widget categories, search, and add widgets to your dashboard
            </DrawerDescription>
          </DrawerHeader>

          <div className="flex-1 flex flex-col min-h-0">
            {/* Category Tabs */}
            <div className="flex-shrink-0 border-b p-2">
              <div className="grid grid-cols-3 gap-1">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className={cn(
                      "flex items-center justify-center gap-1 rounded-lg px-2 py-2 text-xs font-medium transition-colors",
                      activeCategory === cat.id
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                  >
                    <cat.icon className="size-3.5" />
                    <span>{cat.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Search */}
            <div className="flex-shrink-0 p-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
                <Input
                  placeholder="Search widgets..."
                  value={widgetSearch}
                  onChange={e => setWidgetSearch(e.target.value)}
                  className="pl-9 text-sm"
                />
              </div>
            </div>

            {/* Widget List */}
            <div className="flex-1 min-h-0 overflow-y-auto p-2">
              <div className="flex flex-col gap-2">
                {filteredWidgets.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-muted-foreground text-center">
                    <Grid className="size-8 mb-2 opacity-50" />
                    <p className="text-sm font-medium">No widgets found</p>
                    <p className="text-xs mt-1">
                      {Object.keys(widgets).length === 0
                        ? "Start the backend to load widgets"
                        : "Try a different category or search term"}
                    </p>
                  </div>
                ) : (
                  filteredWidgets.map(widget => {
                    const onDashboard = isWidgetOnDashboard(widget.endpoint);
                    return (
                      <Card
                        key={widget.endpoint}
                        className={cn(
                          "p-3 cursor-pointer transition-colors hover:shadow-md group",
                          onDashboard && "ring-2 ring-primary bg-primary/5"
                        )}
                        onClick={() => onDashboard ? removeWidgetFromDashboard(widget.endpoint) : addWidgetToDashboard(widget.endpoint)}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-[10px] px-1.5 py-0 shrink-0">{widget.category}</Badge>
                              <h4 className="font-medium text-sm truncate">{widget.name}</h4>
                            </div>
                            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{widget.description}</p>
                            <div className="flex items-center gap-2 mt-2">
                              <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                                {widget.type === "chart" ? "Chart" : "Table"}
                              </Badge>
                              {onDashboard && (
                                <Badge variant="default" className="text-[10px] px-1.5 py-0">
                                  Added
                                </Badge>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-7 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={e => { e.stopPropagation(); onDashboard ? removeWidgetFromDashboard(widget.endpoint) : addWidgetToDashboard(widget.endpoint); }}
                          >
                            {onDashboard ? <X className="size-4 text-destructive" /> : <Plus className="size-4" />}
                          </Button>
                        </div>
                      </Card>
                    );
                  })
                )}
              </div>
            </div>

            {/* Quick Actions */}
            <DrawerFooter className="p-2 pt-2">
              <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-sm" onClick={() => { setDrawerOpen(false); setRightSidebarOpen(true); }}>
                <Bot className="size-4" />
                Open AI Assistant
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-sm">
                <FolderOpen className="size-4" />
                Load Template
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-sm">
                <History className="size-4" />
                View History
              </Button>
            </DrawerFooter>
          </div>
        </DrawerContent>
      </Drawer>

      {/* Main Content - Dashboard Grid */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="border-b bg-card flex-shrink-0">
          <div className="flex h-16 items-center justify-between px-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setDrawerOpen(true)}
                className="size-9"
                aria-label="Open widget library"
              >
                <PanelLeft className="size-5" />
              </Button>
              <h1 className="text-xl font-bold">OG Terminal</h1>
              
              {/* Template Selector */}
              <div className="w-48">
                <Select value={activeTemplate} onValueChange={v => v !== null && setActiveTemplate(v)}>
                  <SelectTrigger className="w-full">
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
              </div>

              {/* Tab Selector */}
              {template && (
                <div className="hidden md:flex items-center gap-1 bg-muted rounded-lg p-1">
                  {Object.values(template.tabs).map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={cn(
                        "px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
                        activeTab === tab.id
                          ? "bg-background text-foreground shadow-sm"
                          : "text-muted-foreground hover:text-foreground"
                      )}
                    >
                      {tab.name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Global Parameters & Actions */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 hidden sm:flex">
                <label className="text-sm text-muted-foreground">Symbol:</label>
                <Input
                  value={globalParams.symbol}
                  onChange={e => handleGlobalParamChange("symbol", e.target.value.toUpperCase())}
                  placeholder="AAPL"
                  className="w-28"
                />
              </div>
              <div className="flex items-center gap-2 hidden md:flex">
                <label className="text-sm text-muted-foreground">Start:</label>
                <Input
                  type="date"
                  value={globalParams.start_date}
                  onChange={e => handleGlobalParamChange("start_date", e.target.value)}
                  className="w-36"
                />
              </div>
              <div className="flex items-center gap-2 hidden md:flex">
                <label className="text-sm text-muted-foreground">End:</label>
                <Input
                  type="date"
                  value={globalParams.end_date}
                  onChange={e => handleGlobalParamChange("end_date", e.target.value)}
                  className="w-36"
                />
              </div>
              <div className="flex items-center gap-2">
                <label className="text-sm text-muted-foreground">Provider:</label>
                <Select value={dataProvider} onValueChange={handleProviderChange}>
                  <SelectTrigger className="w-28 h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="yfinance">YFinance</SelectItem>
                    <SelectItem value="fmp">FMP</SelectItem>
                    <SelectItem value="polygon">Polygon</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={refreshAllWidgets}
                disabled={layout.some(item => widgetStates[item.i]?.loading)}
                className="gap-1"
              >
                <RefreshCw className={cn("h-4 w-4", layout.some(item => widgetStates[item.i]?.loading) && "animate-spin")} />
                <span className="hidden sm:inline">Refresh All</span>
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setRightSidebarOpen(!rightSidebarOpen)}
                className="h-9 w-9"
                aria-label={rightSidebarOpen ? "Close AI chat" : "Open AI chat"}
              >
                <MessageSquare className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* Mobile Tab Selector */}
          {template && (
            <div className="md:hidden border-t px-2 py-2">
              <div className="flex gap-1 overflow-x-auto bg-muted rounded-lg p-1">
                {Object.values(template.tabs).map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      "px-3 py-1.5 text-xs font-medium rounded-md whitespace-nowrap transition-colors flex-shrink-0",
                      activeTab === tab.id
                        ? "bg-background text-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    {tab.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </header>

        {/* Dashboard - Floating Windows */}
        <div ref={canvasRef} className="flex-1 min-h-0 overflow-hidden relative bg-gray-950">
          {layout.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <LayoutDashboard className="size-16 mb-4 opacity-30" />
              <p className="text-xl font-semibold">No widgets in this tab</p>
              <p className="text-sm mt-2 max-w-md text-center">
                Select widgets from the widget library to add them to your dashboard.
              </p>
              <Button variant="outline" className="mt-6" onClick={() => setDrawerOpen(true)}>
                <Plus className="size-4 mr-2" />
                Browse Widgets
              </Button>
            </div>
          ) : (
            <>
              {layout.map((item, idx) => {
                const widget = widgets[item.i];
                const state = widget ? widgetStates[item.i] : null;

                if (!widget || !state) {
                  return null;
                }

                const zIndex = windowZIndices[item.i] || (10 + idx);
                const defaultPos = { x: 50 + (idx * 30), y: 50 + (idx * 30) };
                const defaultSize = { width: 450, height: 350 };

                return (
                  <DraggableWrapper
                    key={item.i}
                    title={widget.name}
                    defaultPosition={defaultPos}
                    defaultSize={defaultSize}
                    zIndex={zIndex}
                    containerBounds={canvasSize}
                    onFocus={() => bringWindowToFront(item.i)}
                    onPositionChange={(pos) => {
                      // Optional: save position
                    }}
                    onSizeChange={(size) => {
                      // Optional: save size
                    }}
                  >
                    <div className="h-full flex flex-col">
                      {renderParamControls(widget, state)}
                      <div className="flex-1 min-h-0 overflow-auto p-2">
                        {renderWidget(widget, state)}
                      </div>
                    </div>
                  </DraggableWrapper>
                );
              })}
            </>
          )}
        </div>
      </main>

      {/* AI Chat Assistant Drawer */}
      <Drawer
        open={rightSidebarOpen}
        onOpenChange={setRightSidebarOpen}
        showSwipeHandle={isMobile}
        swipeDirection={isMobile ? "down" : "right"}
      >
        <DrawerContent className={cn("flex-col", !isMobile && "[--drawer-content-width:24rem]")}>
          <DrawerHeader className="border-b p-2">
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <Bot className="size-5 text-primary" />
                <DrawerTitle>AI Assistant</DrawerTitle>
              </div>
              <DrawerClose
                render={
                  <Button variant="ghost" size="icon" className="size-8" aria-label="Close assistant" />
                }
              >
                <X className="size-4" />
              </DrawerClose>
            </div>
            <DrawerDescription className="sr-only">
              Chat with the AI assistant about stocks and market data
            </DrawerDescription>
          </DrawerHeader>

          {/* Chat Messages - use native overflow instead of ScrollArea */}
          <div className="flex-1 min-h-0 overflow-y-auto p-4">
            <div className="flex flex-col gap-4">
              {chatMessages.map(msg => (
                <div
                  key={msg.id}
                  className={cn(
                    "flex gap-3 max-w-full",
                    msg.role === "user" ? "flex-row-reverse" : "flex-row"
                  )}
                >
                  <div
                    className={cn(
                      "flex-shrink-0 size-8 rounded-full flex items-center justify-center",
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    )}
                  >
                    {msg.role === "user" ? <User className="size-4" /> : <Bot className="size-4" />}
                  </div>
                  <div
                    className={cn(
                      "max-w-[80%] px-4 py-2 rounded-2xl text-sm",
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground rounded-br-none"
                        : "bg-muted rounded-bl-none"
                    )}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <div className="flex items-center justify-end gap-2 mt-1 text-xs opacity-60">
                      <span>{msg.timestamp.toLocaleTimeString()}</span>
                      {msg.widgets && msg.widgets.length > 0 && (
                        <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                          {msg.widgets.join(", ")}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
          </div>

          {/* Chat Input */}
          <div className="flex-shrink-0 border-t p-4">
            <div className="flex items-end gap-2">
              <div className="flex-1 relative">
                <Textarea
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  onKeyDown={handleChatKeyDown}
                  placeholder="Ask about stocks, market data..."
                  className="min-h-[44px] max-h-32 pr-10 resize-none"
                  rows={1}
                  disabled={chatLoading}
                />
                <div className="absolute bottom-2 right-2 flex items-center gap-1">
                  <Button variant="ghost" size="icon" className="size-7" disabled>
                    <Paperclip className="size-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="size-7" disabled>
                    <Mic className="size-4" />
                  </Button>
                </div>
              </div>
              <Button
                onClick={sendChatMessage}
                disabled={!chatInput.trim() || chatLoading}
                className="size-10 rounded-full flex-shrink-0"
                aria-label="Send message"
              >
                {chatLoading ? <Loader2 className="size-5 animate-spin" /> : <Send className="size-5" />}
              </Button>
            </div>
            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
              <kbd className="px-1.5 py-0.5 bg-muted rounded border text-[10px]">Enter</kbd>
              <span>Send</span>
              <kbd className="px-1.5 py-0.5 bg-muted rounded border text-[10px]">Shift+Enter</kbd>
              <span>New line</span>
            </div>
          </div>
        </DrawerContent>
      </Drawer>
    </div>
  );
}

// Market Heatmap (Recharts Treemap)
interface HeatmapItem {
  symbol: string;
  name: string;
  sector: string;
  marketCap: number | null;
  changePercent: number;
  changeAbsolute: number;
  price: number | null;
  volume: number;
}

interface TreemapDataPoint {
  name: string;
  children?: TreemapDataPoint[];
  size?: number;
  symbol?: string;
  change?: number;
  changeAbsolute?: number;
  price?: number;
  companyName?: string;
  [key: string]: unknown;
}

interface StockHeatmapProps {
  data: { data: HeatmapItem[] };
  widgetParams: Record<string, unknown>;
  onParamChange: (param: string, value: unknown) => void;
}

interface HeatmapWidgetParams {
  sortBy?: string;
  sortOrder?: string;
  sectors?: string;
  animate?: boolean;
}

interface LayoutNode {
  x: number;
  y: number;
  width: number;
  height: number;
  data: TreemapDataPoint;
}

function worstAspectRatio(rowValues: number[], shortSide: number): number {
  if (rowValues.length === 0 || shortSide <= 0) return Infinity;
  const rowSum = rowValues.reduce((a, b) => a + b, 0);
  if (rowSum <= 0) return Infinity;
  const rowLength = rowSum / shortSide;
  let worst = 0;
  for (const v of rowValues) {
    const itemLongSide = (v / rowSum) * rowLength;
    const ratio = Math.max(shortSide / itemLongSide, itemLongSide / shortSide);
    worst = Math.max(worst, ratio);
  }
  return worst;
}

function squarify(data: TreemapDataPoint[], x: number, y: number, width: number, height: number): LayoutNode[] {
  if (!data.length || width <= 0 || height <= 0) return [];
  const totalValue = data.reduce((sum, d) => sum + (d.size || 1), 0);
  if (totalValue <= 0) return [];
  const results: LayoutNode[] = [];
  let remaining = [...data];
  let cx = x, cy = y, cw = width, ch = height;
  while (remaining.length > 0) {
    const isHorizontal = cw >= ch;
    const shortSide = isHorizontal ? ch : cw;
    const remainingTotal = remaining.reduce((sum, d) => sum + (d.size || 1), 0);
    const row: TreemapDataPoint[] = [];
    let rowSum = 0;
    let currentWorst = worstAspectRatio([], shortSide);
    for (let i = 0; i < remaining.length; i++) {
      const newRow = [...row, remaining[i]];
      const newRowSum = rowSum + (remaining[i].size || 1);
      const newWorst = worstAspectRatio(newRow.map(d => d.size || 1), shortSide);
      if (newWorst <= currentWorst) {
        row.push(remaining[i]);
        rowSum = newRowSum;
        currentWorst = newWorst;
      } else {
        break;
      }
    }
    const remainingArea = cw * ch;
    const rowArea = (rowSum / remainingTotal) * remainingArea;
    const rowLength = isHorizontal ? cw : ch;
    const rowThickness = rowArea / rowLength;
    let offset = 0;
    for (const item of row) {
      const itemLength = ((item.size || 1) / rowSum) * rowLength;
      if (isHorizontal) {
        results.push({ x: cx + offset, y: cy, width: itemLength, height: rowThickness, data: item });
      } else {
        results.push({ x: cx, y: cy + offset, width: rowThickness, height: itemLength, data: item });
      }
      offset += itemLength;
    }
    remaining = remaining.slice(row.length);
    if (isHorizontal) {
      cy += rowThickness;
      ch -= rowThickness;
    } else {
      cx += rowThickness;
      cw -= rowThickness;
    }
  }
  return results;
}

function StockHeatmap({ data, widgetParams, onParamChange }: StockHeatmapProps) {
  const params = widgetParams as HeatmapWidgetParams;
  const items = useMemo<HeatmapItem[]>(() => data?.data || [], [data?.data]);
  const [sortBy, setSortBy] = useState<string>(params.sortBy || "pctChange");
  const [sortOrder, setSortOrder] = useState<string>(params.sortOrder || "desc");
  const [selectedSectors, setSelectedSectors] = useState<string[]>(params.sectors ? String(params.sectors).split(",").filter(Boolean) : []);
  const [animate, setAnimate] = useState(params.animate !== false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(entries => {
      const w = entries[0]?.contentRect.width;
      if (w && w > 0) setContainerWidth(w);
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const allSectors = useMemo(() => {
    const sectors = new Set(items.map(i => i.sector).filter(Boolean));
    return Array.from(sectors).sort();
  }, [items]);

  const processedItems = useMemo(() => {
    let result = [...items];
    if (selectedSectors.length > 0) {
      result = result.filter(item => selectedSectors.includes(item.sector));
    }
    result.sort((a, b) => {
      let aVal: number | string = 0;
      let bVal: number | string = 0;
      switch (sortBy) {
        case "pctChange":
          aVal = a.changePercent;
          bVal = b.changePercent;
          break;
        case "absChange":
          aVal = a.changeAbsolute;
          bVal = b.changeAbsolute;
          break;
        case "marketCap":
          aVal = a.marketCap || 0;
          bVal = b.marketCap || 0;
          break;
        case "volume":
          aVal = a.volume;
          bVal = b.volume;
          break;
        case "symbol":
          aVal = a.symbol;
          bVal = b.symbol;
          break;
      }
      if (typeof aVal === "string") {
        return sortOrder === "asc"
          ? (aVal as string).localeCompare(bVal as string)
          : (bVal as string).localeCompare(aVal as string);
      }
      return sortOrder === "asc" ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });
    return result;
  }, [items, sortBy, sortOrder, selectedSectors]);

  const sectors: Record<string, HeatmapItem[]> = {};
  for (const item of processedItems) {
    const s = item.sector || "Other";
    if (!sectors[s]) sectors[s] = [];
    sectors[s].push(item);
  }

  const sectorColors: Record<string, string> = {
    "Technology": "#3b82f6",
    "Healthcare": "#10b981",
    "Financial Services": "#f59e0b",
    "Consumer Cyclical": "#8b5cf6",
    "Communication Services": "#ec4899",
    "Energy": "#ef4444",
    "Industrials": "#6366f1",
    "Consumer Defensive": "#14b8a6",
    "Basic Materials": "#f97316",
    "Real Estate": "#84cc16",
    "Utilities": "#06b6d4",
    "Other": "#6b7280",
  };

  const validItems = processedItems.filter(st => st.marketCap && st.marketCap > 0);
  const maxCap = validItems.length ? Math.max(...validItems.map(st => st.marketCap as number)) : 1;
  const minCap = validItems.length ? Math.min(...validItems.map(st => st.marketCap as number)) : 1;

  const treemapData: TreemapDataPoint[] = validItems.map(st => {
    const cap = st.marketCap as number;
    const normalized = Math.log10(cap / minCap) / Math.log10(maxCap / minCap);
    return {
      name: st.symbol,
      size: 1 + normalized * 99,
      symbol: st.symbol,
      change: st.changePercent || 0,
      changeAbsolute: st.changeAbsolute || 0,
      price: st.price || 0,
      companyName: st.name || st.symbol,
      sector: st.sector || "Other",
    };
  });

  const changeColor = (pct: number): string => {
    if (pct >= 3) return "#0e9f6e";
    if (pct >= 1) return "#22c55e";
    if (pct >= 0) return "#86efac";
    if (pct >= -1) return "#fca5a5";
    if (pct >= -3) return "#ef4444";
    return "#b91c1c";
  };

  const sectorColor = (sector: string): string => {
    return sectorColors[sector] || "#6b7280";
  };

   const layoutNodes = useMemo(() => {
     if (!containerWidth || !treemapData.length) return [];
     const sortedData = [...treemapData];
     // Apply the same sort order as processedItems to maintain consistency
     sortedData.sort((a, b) => {
      let aVal: number | string = 0;
      let bVal: number | string = 0;
       switch (sortBy) {
         case "pctChange":
           aVal = a.change || 0;
           bVal = b.change || 0;
           break;
         case "absChange":
           aVal = a.changeAbsolute || 0;
           bVal = b.changeAbsolute || 0;
           break;
         case "marketCap":
           aVal = a.size || 1;
           bVal = b.size || 1;
           break;
         case "volume":
           // Use symbol name for stable volume-based ordering
           aVal = a.symbol || "";
           bVal = b.symbol || "";
           break;
         case "symbol":
           aVal = a.symbol || "";
           bVal = b.symbol || "";
           break;
       }
       // Apply the same sort order logic as processedItems
       if (typeof aVal === "string") {
         return sortOrder === "asc"
           ? (aVal as string).localeCompare(bVal as string)
           : (bVal as string).localeCompare(aVal as string);
       }
       return sortOrder === "asc" ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
     });
     return squarify(sortedData, 0, 0, containerWidth, 520);
   }, [treemapData, containerWidth, sortBy, sortOrder]);

  const [tooltip, setTooltip] = useState<{ x: number; y: number; data: TreemapDataPoint } | null>(null);

  const handleSortChange = (field: string) => {
    if (sortBy === field) {
      setSortOrder(prev => prev === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
  };

  const toggleSector = (sector: string) => {
    setSelectedSectors(prev =>
      prev.includes(sector)
        ? prev.filter(s => s !== sector)
        : [...prev, sector]
    );
  };

  const isMarketOpen = useMemo(() => {
    const now = new Date();
    const etTime = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));
    const day = etTime.getDay();
    const hour = etTime.getHours();
    const minute = etTime.getMinutes();
    const totalMinutes = hour * 60 + minute;
    return day >= 1 && day <= 5 && totalMinutes >= 9 * 60 + 30 && totalMinutes <= 16 * 60;
  }, []);

  useEffect(() => {
    if (!autoRefresh || !isMarketOpen) return;
    const interval = setInterval(() => {
      onParamChange("_refresh", Date.now());
    }, 15000);
    return () => clearInterval(interval);
  }, [autoRefresh, isMarketOpen, onParamChange]);

  useEffect(() => {
    if (data?.data) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLastUpdate(new Date());
    }
  }, [data?.data]);

  return (
    <div className="w-full min-h-[400px] flex flex-col gap-2">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-2 text-xs px-1">
        <div className="flex items-center gap-1">
          <label className="text-muted-foreground">Sort:</label>
          <Select value={sortBy} onValueChange={v => v && handleSortChange(v)}>
            <SelectTrigger className="w-28 h-7">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="pctChange">% Change</SelectItem>
              <SelectItem value="absChange">Abs Change ($)</SelectItem>
              <SelectItem value="marketCap">Market Cap</SelectItem>
              <SelectItem value="volume">Volume</SelectItem>
              <SelectItem value="symbol">Symbol</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="ghost"
            size="icon"
            className="size-7 p-0"
            onClick={() => handleSortChange(sortBy)}
            title="Toggle sort order"
          >
            {sortOrder === "desc" ? (
              <TrendingUp className="size-4 rotate-180" />
            ) : (
              <TrendingUp className="size-4" />
            )}
          </Button>
        </div>

        <div className="flex items-center gap-1">
          <label className="text-muted-foreground">Sectors:</label>
          <Select
            value={selectedSectors.length === 0 ? "all" : selectedSectors.join(",")}
            onValueChange={v => {
              if (v === "all") {
                setSelectedSectors([]);
              }
            }}
          >
            <SelectTrigger className="w-36 h-7">
              <SelectValue placeholder="All sectors" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Sectors</SelectItem>
              {allSectors.map(sector => (
                <SelectItem key={sector} value={sector}>
                  {sector}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input
              type="checkbox"
              checked={animate}
              onChange={e => setAnimate(e.target.checked)}
              className="rounded border-input h-3 w-3"
            />
            <span className="text-muted-foreground">Animate</span>
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={e => setAutoRefresh(e.target.checked)}
              className="rounded border-input h-3 w-3"
              disabled={!isMarketOpen}
            />
            <span className={cn("text-muted-foreground", !isMarketOpen && "opacity-50")}>
              Auto-refresh (15s)
            </span>
            {!isMarketOpen && (
              <Badge variant="secondary" className="text-[9px] ml-1">Market Closed</Badge>
            )}
          </label>
        </div>

        {lastUpdate && (
          <span className="text-muted-foreground ml-auto">
            Updated: {lastUpdate.toLocaleTimeString()}
          </span>
        )}
      </div>

      {/* Sector Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs px-1">
        {allSectors.map((sector) => {
          const count = processedItems.filter(i => i.sector === sector).length;
          return (
            <label key={sector} className="flex items-center gap-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedSectors.length === 0 || selectedSectors.includes(sector)}
                onChange={e => toggleSector(sector)}
                className="rounded border-input h-3 w-3"
              />
              <span className="font-semibold text-foreground">{sector}</span>
              <span className="text-muted-foreground">({count})</span>
              <span className="w-2.5 h-2.5 rounded-sm inline-block" style={{ backgroundColor: sectorColor(sector) }} />
            </label>
          );
        })}
      </div>

      {/* Treemap */}
      <div ref={containerRef} className="w-full" style={{ height: 520, overflow: "hidden", position: "relative" }}>
        {containerWidth === 0 ? (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground text-xs">
            Loading heatmap...
          </div>
        ) : (
          <svg width={containerWidth} height={520} style={{ display: "block" }}>
            <LayoutGroup>
              {layoutNodes.map((node, i) => {
                const pct = node.data.change || 0;
                const textColor = pct > 0 ? "#052e16" : pct < 0 ? "#450a0a" : "#1f2937";
                const nodeKey = `${node.data.symbol}-${i}`;
                return (
                  <motion.rect
                    key={nodeKey}
                    layout
                    x={node.x}
                    y={node.y}
                    width={node.width}
                    height={node.height}
                    fill={changeColor(pct)}
                    transition={animate ? { type: "spring", stiffness: 300, damping: 30 } : { duration: 0 }}
                    onMouseEnter={() => setTooltip({ x: node.x + node.width / 2, y: node.y + node.height / 2, data: node.data })}
                    onMouseLeave={() => setTooltip(null)}
                    style={{ cursor: "pointer" }}
                  />
                );
              })}
              {layoutNodes.map((node, i) => {
                if (node.width < 50 || node.height < 35) return null;
                const pct = node.data.change || 0;
                const textColor = pct > 0 ? "#052e16" : pct < 0 ? "#450a0a" : "#1f2937";
                const nodeKey = `${node.data.symbol}-${i}`;
                return (
                  <motion.text
                    key={`sym-${nodeKey}`}
                    layout
                    x={node.x + node.width / 2}
                    y={node.y + node.height / 2 - 6}
                    textAnchor="middle"
                    fill={textColor}
                    fontSize={node.width > 80 ? 13 : 10}
                    fontWeight={700}
                    transition={animate ? { type: "spring", stiffness: 300, damping: 30 } : { duration: 0 }}
                  >
                    {node.data.symbol}
                  </motion.text>
                );
              })}
              {layoutNodes.map((node, i) => {
                if (node.width < 50 || node.height < 35) return null;
                const pct = node.data.change || 0;
                const textColor = pct > 0 ? "#052e16" : pct < 0 ? "#450a0a" : "#1f2937";
                const nodeKey = `${node.data.symbol}-${i}`;
                return (
                  <motion.text
                    key={`pct-${nodeKey}`}
                    layout
                    x={node.x + node.width / 2}
                    y={node.y + node.height / 2 + 8}
                    textAnchor="middle"
                    fill={textColor}
                    fontSize={10}
                    opacity={0.85}
                    transition={animate ? { type: "spring", stiffness: 300, damping: 30 } : { duration: 0 }}
                  >
                    {pct >= 0 ? "+" : ""}{pct.toFixed(2)}%
                  </motion.text>
                );
              })}
            </LayoutGroup>
          </svg>
        )}

        {tooltip && (
          <div
            className="absolute bg-popover border rounded-lg p-2 text-xs shadow-md pointer-events-none"
            style={{
              left: tooltip.x,
              top: tooltip.y,
              transform: "translate(-50%, -100%)",
              zIndex: 50,
            }}
          >
            <div className="font-bold">{tooltip.data.symbol}</div>
            <div className="text-muted-foreground">{tooltip.data.companyName}</div>
            {typeof tooltip.data.sector === "string" && <div className="text-muted-foreground/80">{tooltip.data.sector}</div>}
            <div>Price: ${tooltip.data.price?.toFixed(2)}</div>
            <div>Abs Change: ${tooltip.data.changeAbsolute?.toFixed(2)}</div>
            <div className={(tooltip.data.change ?? 0) >= 0 ? "text-emerald-600" : "text-red-600"}>
              {(tooltip.data.change ?? 0) >= 0 ? "+" : ""}{(tooltip.data.change ?? 0).toFixed(2)}%
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

interface PlotlyChartProps {
  data: unknown;
}

interface ColumnDef {
  field: string;
  headerName?: string;
  renderFn?: string;
}

interface DataTableProps {
  data: unknown;
  columns: ColumnDef[];
}

// Simple Plotly chart renderer
let plotlyModule: { Plots: { resize: (el: HTMLElement) => void }; newPlot: (...args: unknown[]) => void } | null = null;

function PlotlyChart({ data }: PlotlyChartProps) {
  const ref = useRef<HTMLDivElement | null>(null);
  
  useEffect(() => {
    if (!ref.current || !data) return;
    
    // Dynamic import of plotly.js-dist
    import("plotly.js-dist").then(Plotly => {
      plotlyModule = Plotly as unknown as typeof plotlyModule;
      const plotData = (data as Record<string, unknown>).data || data;
      const plotLayout = (data as Record<string, unknown>).layout || {};
      Plotly.newPlot(ref.current!, plotData as unknown as Plotly.Data[], plotLayout as Plotly.Layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ["lasso2d", "select2d"],
      });
    });
  }, [data]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let raf = 0;
    const ro = new ResizeObserver(() => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        if (plotlyModule && el.querySelector(".js-plotly-plot")) {
          plotlyModule.Plots.resize(el);
        }
      });
    });
    ro.observe(el);
    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
    };
  }, []);

  return <div ref={ref} style={{ width: "100%", height: "100%", minHeight: "300px" }} />;
}

// Data table component
function DataTable({ data, columns }: DataTableProps) {
  if (!data) {
    return <div className="text-center text-muted-foreground py-8">No data</div>;
  }

  // Normalize data to array
  let rows: Record<string, unknown>[];
  if (Array.isArray(data)) {
    rows = data;
  } else if (typeof data === 'object') {
    rows = Object.values(data);
  } else {
    return <div className="text-center text-muted-foreground py-8">No data</div>;
  }

  if (rows.length === 0) {
    return <div className="text-center text-muted-foreground py-8">No data</div>;
  }

  const cols = columns.length > 0 ? columns : Object.keys(rows[0]).map(key => ({ field: key, headerName: key, renderFn: undefined }));

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
          {rows.map((row, rowIdx) => {
            const rowKey = `${row.id || row.symbol || row.name || 'row'}-${rowIdx}`;
            return (
              <tr key={rowKey} className="border-b hover:bg-muted/50">
                {cols.map(col => {
                  const value = row[col.field];

                  if (col.renderFn === "link" && typeof value === "string") {
                    return (
                      <td key={col.field} className="p-2">
                        <a href={value} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                          Link
                        </a>
                      </td>
                    );
                  }

                  if (col.renderFn === "percent" && typeof value === "number") {
                    return (
                      <td key={col.field} className="p-2">
                        {`${(value * 100).toFixed(2)}%`}
                      </td>
                    );
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
                      {value !== undefined && value !== null ? String(value) : "—"}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}