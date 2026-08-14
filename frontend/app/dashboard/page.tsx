"use client";

import { useState, useEffect, useRef } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, RefreshCw, Search, ChevronDown, ChevronUp, BarChart3, LineChart, PieChart, Table, Settings, Grid, LayoutDashboard, MessageSquare, ChevronLeft, ChevronRight, X, Plus, FolderOpen, History, Bot, User, Send, Mic, Paperclip, Settings as SettingsIcon } from "lucide-react";
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

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  widgets?: string[];
}

// Use relative paths for Next.js rewrites to work
const API_BASE = "";

const CATEGORIES = [
  { id: "equity", name: "Equity", icon: BarChart3 },
  { id: "macro", name: "Macro", icon: LineChart },
  { id: "news", name: "News", icon: MessageSquare },
  { id: "options", name: "Options", icon: PieChart },
  { id: "portfolio", name: "Portfolio", icon: Table },
  { id: "godel", name: "Godel Terminal", icon: Settings },
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
      content: "Welcome to Godel Terminal! I'm your AI financial assistant. Ask me about stocks, market data, technical analysis, or create custom widgets.",
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

  const loadWidgetsAndTemplates = async () => {
    try {
      const [widgetsRes, templatesRes] = await Promise.all([
        fetch(`/widgets.json`),
        fetch(`/templates.json`),
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
  const filteredWidgets = getFilteredWidgets();
  const isWidgetOnDashboard = (endpoint: string) => layout.some(item => item.i === endpoint);

  return (
    <div className="flex h-screen bg-background">
      {/* Left Sidebar - Widget Library / Navigation */}
      <aside
        className={cn(
          "flex flex-col border-r bg-card transition-all duration-300",
          leftSidebarOpen ? "w-80" : "w-16"
        )}
      >
        <div className="flex h-16 items-center justify-between border-b p-4">
          {leftSidebarOpen && (
            <h2 className="text-lg font-semibold">Widget Library</h2>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
            className="h-8 w-8"
            aria-label={leftSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            {leftSidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>

        {leftSidebarOpen && (
          <div className="flex-1 overflow-hidden flex flex-col">
            {/* Category Tabs */}
            <div className="border-b p-2">
              <Tabs value={activeCategory} onValueChange={setActiveCategory} className="w-full">
                <TabsList className="grid w-full gap-1 bg-muted p-1" role="tablist">
                  {CATEGORIES.map(cat => (
                    <TabsTrigger
                      key={cat.id}
                      value={cat.id}
                      className="flex items-center justify-center gap-1 text-xs py-2"
                      role="tab"
                    >
                      <cat.icon className="h-3.5 w-3.5" />
                      <span className="hidden sm:inline">{cat.name}</span>
                    </TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            </div>

            {/* Search */}
            <div className="p-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search widgets..."
                  value={widgetSearch}
                  onChange={e => setWidgetSearch(e.target.value)}
                  className="pl-9 text-sm"
                />
              </div>
            </div>

            {/* Widget List */}
            <ScrollArea className="flex-1 p-2">
              <div className="space-y-2">
                {filteredWidgets.map(widget => {
                  const onDashboard = isWidgetOnDashboard(widget.endpoint);
                  return (
                    <Card
                      key={widget.endpoint}
                      className={cn(
                        "p-3 cursor-pointer transition-all hover:shadow-md",
                        onDashboard && "ring-2 ring-primary bg-primary/5"
                      )}
                      onClick={() => onDashboard ? removeWidgetFromDashboard(widget.endpoint) : addWidgetToDashboard(widget.endpoint)}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground uppercase">{widget.category}</span>
                            <h4 className="font-medium text-sm truncate">{widget.name}</h4>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 truncate">{widget.description}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className={cn(
                              "px-1.5 py-0.5 text-xs rounded",
                              widget.type === "chart" ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"
                            )}>
                              {widget.type === "chart" ? "Chart" : "Table"}
                            </span>
                            {onDashboard && (
                              <span className="px-1.5 py-0.5 text-xs rounded bg-primary/10 text-primary">
                                Added
                              </span>
                            )}
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={e => { e.stopPropagation(); onDashboard ? removeWidgetFromDashboard(widget.endpoint) : addWidgetToDashboard(widget.endpoint); }}
                        >
                          {onDashboard ? <X className="h-4 w-4 text-destructive" /> : <Plus className="h-4 w-4 text-primary" />}
                        </Button>
                      </div>
                    </Card>
                  );
                })}
              </div>
            </ScrollArea>

            {/* Quick Actions */}
            <Separator className="mx-2" />
            <div className="p-2 space-y-1">
              <Button variant="outline" className="w-full justify-start gap-2 text-sm" onClick={() => setRightSidebarOpen(true)}>
                <Bot className="h-4 w-4" />
                Open AI Assistant
              </Button>
              <Button variant="outline" className="w-full justify-start gap-2 text-sm">
                <FolderOpen className="h-4 w-4" />
                Load Template
              </Button>
              <Button variant="outline" className="w-full justify-start gap-2 text-sm">
                <History className="h-4 w-4" />
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
                <Tabs value={activeTab} onValueChange={setActiveTab} className="hidden md:flex">
                  <TabsList className="gap-1 bg-muted p-1">
                    {Object.values(template.tabs).map(tab => (
                      <TabsTrigger key={tab.id} value={tab.id} className="text-sm px-3">
                        {tab.name}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </Tabs>
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
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full gap-1 bg-muted p-1">
                  {Object.values(template.tabs).map(tab => (
                    <TabsTrigger key={tab.id} value={tab.id} className="text-xs py-2">
                      {tab.name}
                    </TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            </div>
          )}
        </header>

        {/* Dashboard Grid */}
        <div className="flex-1 overflow-auto p-4">
          {layout.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <LayoutDashboard className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-lg font-medium">No widgets in this tab</p>
              <p className="text-sm">Select widgets from the left sidebar to add them to your dashboard</p>
              <Button variant="outline" className="mt-4" onClick={() => setLeftSidebarOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Browse Widgets
              </Button>
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
                      <Button variant="outline" size="sm" className="mt-2" onClick={() => removeWidgetFromDashboard(item.i)}>
                        Remove
                      </Button>
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
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeWidgetFromDashboard(widget.endpoint)}
                          className="h-7 w-7 text-destructive hover:text-destructive"
                        >
                          <X className="h-4 w-4" />
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
      </main>

      {/* Right Sidebar - AI Chat Assistant */}
      <aside
        className={cn(
          "flex flex-col border-l bg-card transition-all duration-300",
          rightSidebarOpen ? "w-96" : "w-0 overflow-hidden"
        )}
      >
        {rightSidebarOpen && (
          <div className="flex flex-col h-full">
            <div className="flex h-16 items-center justify-between border-b p-4">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-semibold">AI Assistant</h2>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setRightSidebarOpen(false)}
                className="h-8 w-8"
                aria-label="Close chat"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Chat Messages */}
            <ScrollArea className="flex-1 p-4 space-y-4">
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
                      "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium",
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    )}
                  >
                    {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
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
                        <span className="px-2 py-0.5 bg-primary/20 text-primary rounded text-xs">
                          {msg.widgets.join(", ")}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </ScrollArea>

            {/* Chat Input */}
            <div className="border-t p-4">
              <div className="flex items-end gap-2">
                <div className="flex-1 relative">
                  <Textarea
                    value={chatInput}
                    onChange={e => setChatInput(e.target.value)}
                    onKeyDown={handleChatKeyDown}
                    placeholder="Ask about stocks, market data, analysis..."
                    className="min-h-[44px] max-h-32 pr-10 resize-none"
                    rows={1}
                    disabled={chatLoading}
                  />
                  <div className="absolute bottom-2 right-2 flex items-center gap-1">
                    <Button variant="ghost" size="icon" className="h-7 w-7" disabled>
                      <Paperclip className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7" disabled>
                      <Mic className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <Button
                  onClick={sendChatMessage}
                  disabled={!chatInput.trim() || chatLoading}
                  className="h-10 w-10 rounded-full"
                  aria-label="Send message"
                >
                  {chatLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
                </Button>
              </div>
              <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                <kbd className="px-1.5 py-0.5 bg-muted rounded border">Enter</kbd> Send
                <kbd className="px-1.5 py-0.5 bg-muted rounded border">Shift+Enter</kbd> New line
              </div>
            </div>
          </div>
        )}
      </aside>
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