import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Armchair, ArrowRight, Sparkles } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_-10%,oklch(0.76_0.14_72/0.14),transparent)]"
      />
      <header className="absolute top-0 w-full max-w-6xl px-6 py-8 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="grid size-9 place-items-center rounded-xl bg-primary text-primary-foreground">
            <Armchair className="size-5" />
          </span>
          <span className="font-heading text-lg font-semibold tracking-tight">
            FurniCost
          </span>
        </Link>
        <Button variant="outline" size="sm" render={<Link href="/workspace" />}>
          Open Workspace
        </Button>
      </header>

      <section className="relative z-10 mx-auto flex max-w-3xl flex-col items-center text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-card/60 px-4 py-1.5 text-sm text-muted-foreground">
          <Sparkles className="size-3.5 text-primary" />
          AI-driven manufacturing cost estimation
        </div>
        <h1 className="font-heading text-balance text-5xl font-semibold tracking-tight sm:text-6xl">
          Know what it costs to{" "}
          <em className="italic text-primary">make</em>, before you make it.
        </h1>
        <p className="mt-6 max-w-xl text-balance text-lg text-muted-foreground">
          Itemized cost breakdowns for furniture manufacturing — BOM, labor,
          machine time, and overhead — with AI-generated justification for every
          line. Adjust parameters. Simulate scenarios. Export reports.
        </p>
        <div className="mt-10 flex items-center gap-4">
          <Button size="lg" render={<Link href="/workspace" />}>
            Build an estimate
            <ArrowRight className="ml-2 size-4" />
          </Button>
          <Button size="lg" variant="outline" render={<Link href="/workspace" />}>
            Explore the demo
          </Button>
        </div>
      </section>
    </main>
  );
}
