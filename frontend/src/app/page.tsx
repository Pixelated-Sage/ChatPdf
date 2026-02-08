'use client';

import Link from "next/link";
import { motion } from "framer-motion";
import { MessageSquare, ArrowRight, Shield, Zap, Sparkles, Files, Layers, Search } from "lucide-react";

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Background Ambience */}
      <div className="absolute left-1/2 top-0 -z-10 h-[800px] w-[800px] -translate-x-1/2 rounded-full bg-primary/20 opacity-30 blur-[120px]" />
      <div className="absolute right-0 bottom-0 -z-10 h-[600px] w-[600px] translate-x-1/3 rounded-full bg-indigo-500/10 opacity-30 blur-[100px]" />

      {/* Navigation */}
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Sparkles size={18} />
          </div>
          <span className="text-xl font-bold tracking-tight">ChatPDF</span>
        </div>
        <Link href="/upload" className="text-sm font-semibold leading-6 text-foreground hover:text-primary transition-colors">
          Log in <span aria-hidden="true">&rarr;</span>
        </Link>
      </nav>

      {/* Hero Section */}
      <div className="relative mx-auto max-w-7xl px-6 pt-16 sm:pt-24 lg:px-8 lg:pt-32">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="mx-auto max-w-2xl text-center"
        >
          <div className="mb-8 flex justify-center">
            <div className="relative rounded-full px-3 py-1 text-sm leading-6 text-muted-foreground ring-1 ring-border glass hover:bg-accent/50 transition-all cursor-default">
              <span className="font-semibold text-primary">New v2.0</span> is now available.
            </div>
          </div>
          
          <h1 className="text-5xl font-extrabold tracking-tight text-foreground sm:text-7xl text-balance">
            Chat with your documents <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-violet-400">instantly</span>
          </h1>
          
          <p className="mt-6 text-lg leading-8 text-muted-foreground text-balance">
            Stop scrolling through endless pages. Upload PDFs, ask questions, and get precise answers with source citations in seconds.
          </p>
          
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link
              href="/upload"
              className="rounded-xl bg-primary px-8 py-3.5 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/25 ring-1 ring-primary/50 transition-all hover:scale-105 hover:bg-primary/90 hover:shadow-primary/40"
            >
              Get Started
            </Link>
            <Link href="#features" className="group text-sm font-semibold leading-6 text-foreground inline-flex items-center gap-1 hover:text-primary transition-colors">
              View Features <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </motion.div>

        {/* Feature Grid */}
        <div id="features" className="mx-auto mt-32 max-w-7xl px-6 sm:mt-40 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-primary">Supercharged Research</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Understand complex documents faster
            </p>
          </div>
          
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <div className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3">
              {[
                {
                  name: "Smart Context",
                  description: "Our RAG engine retrieves the most relevant paragraphs from multiple files to answer your exact question.",
                  icon: Layers,
                },
                {
                  name: "Instant Citations",
                  description: "Don't just trust the AI. Click on any citation to verify the source directly in the original PDF.",
                  icon: Search,
                },
                {
                  name: "Secure Processing",
                  description: "Your documents are processed locally in a sandboxed environment and are never used for training.",
                  icon: Shield,
                },
              ].map((feature) => (
                <div key={feature.name} className="relative pl-16 group">
                  <dt className="text-base font-semibold leading-7 text-foreground">
                    <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 ring-1 ring-primary/20 group-hover:bg-primary/20 transition-colors">
                      <feature.icon className="h-5 w-5 text-primary" aria-hidden="true" />
                    </div>
                    {feature.name}
                  </dt>
                  <dd className="mt-2 text-base leading-7 text-muted-foreground">
                    {feature.description}
                  </dd>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Decoration */}
      <footer className="mt-32 border-t border-border/50 py-12">
        <div className="mx-auto max-w-7xl px-6 text-center text-sm text-muted-foreground opacity-60">
          <p>© 2026 ChatPDF AI. Built with Next.js 14 and Gemini Pro.</p>
        </div>
      </footer>
    </div>
  );
}
