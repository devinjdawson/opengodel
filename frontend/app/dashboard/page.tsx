"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, RefreshCw, Search, BarChart3, LineChart, PieChart, Table, Settings, Grid, LayoutDashboard, MessageSquare, ChevronLeft, ChevronRight, X, Plus, FolderOpen, History, Bot, User, Send, Mic, Paperclip, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

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
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);
  const [rightSidebarOpen, setRightSidebarOpen] = useState(true);
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

  // Load widgets and templates on mount
  useEffect(() => {
    loadWidgetsAndTemplates();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

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
      
      let rawWidgets: any = null;
      let templatesData: any = null;
      
      if (widgetsRes.ok) rawWidgets = await widgetsRes.json();
      if (templatesRes.ok) templatesData = await templatesRes.json();
      
      let widgetsArray: any[];
      if (Array.isArray(rawWidgets)) {
        widgetsArray = rawWidgets;
      } else if (rawWidgets && typeof rawWidgets === "object") {
        widgetsArray = Object.values(rawWidgets);
      } else {
        widgetsArray = [];
      }
      
      const widgetsObj: Record<string, WidgetConfig> = {};
      for (const widget of widgetsArray) {
        if (widget.endpoint) widgetsObj[widget.endpoint] = widget;
      }
      
      setWidgets(widgetsObj);
      setTemplates(Array.isArray(templatesData) ? templatesData : []);
      
      const initialStates: Record<string, WidgetState> = {};
      for (const widget of widgetsArray) {
        if (!widget.endpoint) continue;
        const params: Record<string, string | number | boolean> = {};
        for (const param of widget.params || []) {
          params[param.paramName] = param.value;
        }
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

      const response = await fetch(`/api/v1/widgets/${widget.category.toLowerCase()}/${endpoint}?${params}`);
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
      const response = await fetch(`/api/v1/agent/chat`, {
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

    if (widget.type === "chart" && state.data) {
      return <PlotlyChart data={state.data} />;
    }

    if (widget.type === "heatmap" && state.data) {
      return <StockHeatmap data={state.data} />;
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
      {/* Left Sidebar - Widget Library / Navigation */}
      <aside
        className={cn(
          "flex flex-col border-r bg-card flex-shrink-0 overflow-hidden",
          leftSidebarOpen ? "w-80" : "w-16"
        )}
      >
        <div className="flex h-16 flex-shrink-0 items-center justify-between border-b px-4">
          {leftSidebarOpen && (
            <h2 className="text-lg font-semibold truncate">Widget Library</h2>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
            className="size-8"
            aria-label={leftSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            {leftSidebarOpen ? <ChevronLeft className="size-4" /> : <ChevronRight className="size-4" />}
          </Button>
        </div>

        {leftSidebarOpen && (
          <div className="flex-1 flex flex-col min-h-0">
            {/* Category Tabs - Use buttons instead of Base UI Tabs */}
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
            <Separator />
            <div className="flex-shrink-0 p-2 flex flex-col gap-1">
              <Button variant="outline" size="sm" className="w-full justify-start gap-2 text-sm" onClick={() => setRightSidebarOpen(true)}>
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
            </div>
          </div>
        )}
      </aside>

      {/* Main Content - Dashboard Grid */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="border-b bg-card flex-shrink-0">
          <div className="flex h-16 items-center justify-between px-4">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold">OpenBB Financial Dashboard</h1>
              
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
                aria-label={rightSidebarOpen ? "Close chat" : "Open chat"}
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

        {/* Dashboard Grid */}
        <div className="flex-1 min-h-0 overflow-auto p-4">
          {layout.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[60vh] text-muted-foreground">
              <LayoutDashboard className="size-16 mb-4 opacity-30" />
              <p className="text-xl font-semibold">No widgets in this tab</p>
              <p className="text-sm mt-2 max-w-md text-center">
                Select widgets from the left sidebar to add them to your dashboard, or check that the backend is running.
              </p>
              <Button variant="outline" className="mt-6" onClick={() => setLeftSidebarOpen(true)}>
                <Plus className="size-4 mr-2" />
                Browse Widgets
              </Button>
            </div>
          ) : (
            <div className="grid gap-4" style={{ gridTemplateColumns: "repeat(12, minmax(0, 1fr))" }}>
              {layout.map((item, idx) => {
                const widget = widgets[item.i];
                const state = widget ? widgetStates[item.i] : null;
                const itemKey = `${item.i}-${idx}`;

                if (!widget || !state) {
                  return (
                    <Card
                      key={itemKey}
                      className="p-4 border-destructive/50"
                      style={{
                        gridColumn: `span ${Math.min(12, Math.max(1, Math.round(item.w / 100 * 12)))}`,
                      }}
                    >
                      <div className="flex flex-col gap-2">
                        <p className="text-sm text-destructive">Widget not found: <code>{item.i}</code></p>
                        <Button variant="destructive" size="sm" className="w-fit" onClick={() => removeWidgetFromDashboard(item.i)}>
                          Remove
                        </Button>
                      </div>
                    </Card>
                  );
                }

                const colSpan = Math.min(12, Math.max(1, Math.round(item.w / 100 * 12)));

                return (
                  <Card
                    key={itemKey}
                    className="flex flex-col overflow-hidden min-h-[200px]"
                    style={{
                      gridColumn: `span ${colSpan}`,
                    }}
                  >
                    <CardHeader className="flex flex-row items-center justify-between px-4 py-3 pb-2">
                      <CardTitle className="text-base font-semibold truncate">{widget.name}</CardTitle>
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <Badge variant="outline" className="text-[10px] px-1.5 py-0">{widget.category}</Badge>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => refreshWidget(widget.endpoint)}
                          disabled={state.loading}
                          className="size-7"
                        >
                          <RefreshCw className={cn("size-4", state.loading && "animate-spin")} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeWidgetFromDashboard(widget.endpoint)}
                          className="size-7 text-destructive hover:text-destructive"
                        >
                          <X className="size-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col px-4 pb-4 pt-0 min-h-0">
                      {renderParamControls(widget, state)}
                      <div className="flex-1 min-h-0 mt-2 overflow-hidden">
                        {renderWidget(widget, state)}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </main>

      {/* Right Sidebar - AI Chat Assistant */}
      {rightSidebarOpen && (
        <aside className="flex flex-col border-l bg-card flex-shrink-0 w-96 h-full">
          <div className="flex h-16 flex-shrink-0 items-center justify-between border-b px-4">
            <div className="flex items-center gap-2">
              <Bot className="size-5 text-primary" />
              <h2 className="text-lg font-semibold">AI Assistant</h2>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setRightSidebarOpen(false)}
              className="size-8"
              aria-label="Close chat"
            >
              <X className="size-4" />
            </Button>
          </div>

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
        </aside>
      )}
    </div>
  );
}

// Market Heatmap (Recharts Treemap)
function StockHeatmap({ data }: { data: any }) {
  const items: any[] = data?.data || [];
  if (items.length === 0) {
    return <div className="text-center text-muted-foreground py-8">No heatmap data</div>;
  }

  const sectors: Record<string, any[]> = {};
  for (const item of items) {
    const s = item.sector || "Other";
    if (!sectors[s]) sectors[s] = [];
    sectors[s].push(item);
  }

  const treemapData = Object.entries(sectors).map(([sector, stocks]) => ({
    name: sector,
    children: stocks.map(st => ({
      name: st.symbol,
      size: Math.max(st.marketCap || 1, 1000000),
      symbol: st.symbol,
      change: st.changePercent || 0,
      price: st.price || 0,
      companyName: st.name || st.symbol,
    })),
  }));

  const changeColor = (pct: number) => {
    if (pct >= 3) return "#0e9f6e";
    if (pct >= 1) return "#22c55e";
    if (pct >= 0) return "#86efac";
    if (pct >= -1) return "#fca5a5";
    if (pct >= -3) return "#ef4444";
    return "#b91c1c";
  };

  const CustomContent = (props: any) => {
    const { x, y, width, height, name, change, price, symbol } = props;
    if (!width || !height || width < 30 || height < 20) return null;
    const bg = changeColor(change || 0);
    const textColor = change > 0 ? "#052e16" : change < 0 ? "#450a0a" : "#1f2937";

    return (
      <g>
        <rect x={x} y={y} width={width} height={height} fill={bg} stroke="#fff" strokeWidth={1} rx={2} />
        {width > 45 && height > 30 && (
          <>
            <text x={x + width / 2} y={y + height / 2 - 6} textAnchor="middle" fill={textColor} fontSize={width > 70 ? 13 : 10} fontWeight={700}>
              {symbol}
            </text>
            <text x={x + width / 2} y={y + height / 2 + 8} textAnchor="middle" fill={textColor} fontSize={10} opacity={0.85}>
              {change >= 0 ? "+" : ""}{change.toFixed(2)}%
            </text>
          </>
        )}
      </g>
    );
  };

  const { Treemap, ResponsiveContainer, Tooltip } = require("recharts");

  return (
    <div className="w-full h-full min-h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <Treemap
          data={treemapData}
          dataKey="size"
          aspectRatio={4 / 3}
          stroke="#fff"
          content={<CustomContent />}
          isAnimationActive={false}
        >
          <Tooltip
            content={({ active, payload }: any) => {
              if (!active || !payload?.length) return null;
              const d = payload[0]?.payload;
              if (!d?.symbol) return null;
              return (
                <div className="bg-popover border rounded-lg p-2 text-xs shadow-md">
                  <div className="font-bold">{d.symbol}</div>
                  <div className="text-muted-foreground">{d.companyName}</div>
                  <div>Price: ${d.price?.toFixed(2)}</div>
                  <div className={d.change >= 0 ? "text-emerald-600" : "text-red-600"}>
                    {d.change >= 0 ? "+" : ""}{d.change?.toFixed(2)}%
                  </div>
                </div>
              );
            }}
          />
        </Treemap>
      </ResponsiveContainer>
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
function DataTable({ data, columns }: { data: any; columns: any[] }) {
  if (!data) {
    return <div className="text-center text-muted-foreground py-8">No data</div>;
  }

  // Normalize data to array
  let rows: any[];
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

  const cols = columns.length > 0 ? columns : Object.keys(rows[0]).map(key => ({ field: key, headerName: key }));

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
            const rowKey = row.id || row.symbol || row.name || rowIdx;
            return (
              <tr key={rowKey} className="border-b hover:bg-muted/50">
                {cols.map(col => {
                  const value = row[col.field];

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
                      {value ?? "—"}
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