"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot, MessageSquare, Sparkles, Code, Brain, Globe } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Page() {
  const features = [
    {
      icon: Bot,
      title: "AI Chat Interface",
      description: "Built with ai-elements components for streaming responses, reasoning, and tool display",
      href: "/chat",
    },
    {
      icon: Sparkles,
      title: "Modern UI",
      description: "shadcn/ui with Base UI primitives, Tailwind v4, and Next.js 16",
      href: "/chat",
    },
    {
      icon: Brain,
      title: "Multiple Models",
      description: "Switch between OpenAI, Anthropic, and Google models with the ModelSelector",
      href: "/chat",
    },
    {
      icon: Code,
      title: "Code Blocks",
      description: "Syntax-highlighted code blocks with copy functionality",
      href: "/chat",
    },
    {
      icon: MessageSquare,
      title: "Rich Messages",
      description: "Support for sources, reasoning, attachments, and branching conversations",
      href: "/chat",
    },
    {
      icon: Globe,
      title: "Web Search",
      description: "Toggle web search integration for up-to-date information",
      href: "/chat",
    },
  ];

  return (
    <div className="flex min-h-svh flex-col items-center justify-center p-6 bg-background">
      <div className="flex w-full max-w-4xl flex-col items-center gap-8">
        <div className="text-center">
          <h1 className="mb-4 text-4xl font-bold tracking-tight">
            OpenGodel <span className="text-primary">AI</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl">
            A modern AI chat interface built with Next.js 16, shadcn/ui (Base UI),
            and Vercel's ai-elements components. Features streaming responses,
            reasoning display, code blocks, and multi-model support.
          </p>
        </div>

        <Link href="/chat" className="w-full">
          <Button size="lg" className="w-full gap-2">
            <Sparkles className="size-5" />
            Start Chatting
          </Button>
        </Link>

        <div className="grid w-full gap-4 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Link key={feature.title} href={feature.href} className="group">
              <Card className={cn(
                "transition-all duration-200 hover:border-primary/50 hover:shadow-lg",
                "bg-card"
              )}>
                <CardHeader>
                  <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary/20">
                    <feature.icon className="size-5" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        <div className="flex w-full items-center justify-between border-t pt-6 text-sm text-muted-foreground">
          <span>Built with Next.js 16 • shadcn/ui (Base) • ai-elements • Tailwind v4</span>
          <span className="font-mono">(Press <kbd className="px-1.5 py-0.5 rounded bg-muted">d</kbd> to toggle dark mode)</span>
        </div>
      </div>
    </div>
  );
}