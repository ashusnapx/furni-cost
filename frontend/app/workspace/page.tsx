import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Armchair,
  Bot,
  FileText,
  FlaskConical,
  GitBranch,
  LayoutGrid,
  ReceiptText,
} from "lucide-react";

const nav = [
  { label: "BOM Configurator", href: "#bom", icon: GitBranch },
  { label: "Cost Breakdown", href: "#breakdown", icon: ReceiptText },
  { label: "Scenario Lab", href: "#scenarios", icon: FlaskConical },
  { label: "AI Explainer", href: "#ai", icon: Bot },
  { label: "Reports", href: "#reports", icon: FileText },
];

export default function WorkspacePage() {
  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 flex h-screen w-60 shrink-0 flex-col border-r bg-sidebar">
        <Link
          href="/"
          className="flex items-center gap-2.5 px-5 py-6 border-b"
        >
          <span className="grid size-8 place-items-center rounded-lg bg-primary text-primary-foreground">
            <Armchair className="size-4" />
          </span>
          <span className="font-heading text-base font-semibold tracking-tight">
            FurniCost
          </span>
        </Link>
        <nav className="flex flex-col gap-1 p-3">
          {nav.map(({ label, href, icon: Icon }) => (
            <a
              key={label}
              href={href}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            >
              <Icon className="size-4" />
              {label}
            </a>
          ))}
        </nav>
        <div className="mt-auto p-4">
          <div className="flex items-center gap-2 rounded-lg border bg-card/60 p-3 text-xs text-muted-foreground">
            <LayoutGrid className="size-3.5" />
            Workspace · M0 skeleton
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b bg-background/80 px-8 backdrop-blur">
          <div>
            <h1 className="font-heading text-lg font-semibold tracking-tight">
              Estimate Workspace
            </h1>
            <p className="text-xs text-muted-foreground">
              New product cost estimate · draft
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="secondary">Draft</Badge>
            <Button size="sm" disabled>
              Run estimate
            </Button>          </div>
        </header>

        <div className="grid gap-6 p-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Getting started</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <p>
                Milestone 0 scaffold complete. Cost engine, agents, and UI
                surfaces land in M1–M5.
              </p>
              <div className="grid gap-2 text-xs">
                <p>
                  <span className="text-primary">M1</span> — synthetic data,
                  Neo4j knowledge graph, ABC cost engine
                </p>
                <p>
                  <span className="text-primary">M2</span> — MCP server,
                  LangGraph supervisor, SSE streaming, Langfuse tracing
                </p>
                <p>
                  <span className="text-primary">M3</span> — PageIndex
                  vectorless RAG for spec sheets
                </p>
                <p>
                  <span className="text-primary">M4</span> — cockpit UI: BOM
                  tree, breakdown, scenario lab
                </p>
                <p>
                  <span className="text-primary">M5</span> — AI explainer chat,
                  report export, accuracy eval loop
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
