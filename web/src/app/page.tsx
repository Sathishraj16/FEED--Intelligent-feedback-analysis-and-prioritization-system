'use client';

import Link from "next/link";

export default function Landing() {
  return (
    <main className="min-h-screen bg-white text-black">
      {/* Hero with background image */}
      <section className="relative overflow-hidden">
        {/* Background PNG from public/assets. Replace filename as needed. */}
        <div
          className="absolute inset-0"
          style={{
            backgroundColor: '#f5f5f5',
            backgroundImage: `url(/assets/home-hero.png)`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'saturate(0.95)',
          }}
        >
          <div
            className="absolute inset-0"
            style={{
              background:
                'repeating-linear-gradient(45deg, rgba(0,0,0,0), rgba(0,0,0,0) 35px, rgba(0,0,0,0.03) 35px, rgba(0,0,0,0.03) 70px)'
            }}
          />
        </div>
        <div className="relative mx-auto max-w-5xl px-6 py-24 md:py-32">
          <div className="max-w-2xl">
            <h1 className="text-5xl md:text-6xl font-medium tracking-tight leading-tight text-black">
              Focus on the right feedback
            </h1>
            <p className="mt-6 text-xl leading-relaxed" style={{ color: '#434343' }}>
              FEED ingests feedback from anywhere, scores it for sentiment, urgency, and impact, then delivers a weekly prioritized action list.
            </p>
            <div className="mt-10">
              <Link
                href="/feed"
                className="px-6 py-3 rounded-md text-white text-sm font-medium hover:opacity-90 transition-opacity inline-block"
                style={{ backgroundColor: '#000000' }}
              >
                Try the App
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Value Proposition */}
      <section className="border-t" style={{ borderColor: '#e5e5e5', backgroundColor: '#000000' }}>
        <div className="mx-auto max-w-3xl px-6 py-20 text-center">
          <h2 className="text-3xl font-medium leading-tight text-white">Stop drowning in feedback</h2>
          <p className="mt-6 leading-relaxed text-lg" style={{ color: '#b0b0b0' }}>
            Product teams receive hundreds of messages across Slack, email, support tickets, and user interviews. Important insights get buried. Critical issues slip through the cracks.
          </p>
          <p className="mt-4 leading-relaxed text-lg" style={{ color: '#b0b0b0' }}>
            FEED centralizes everything, automatically identifies what matters most, and helps you take action on the feedback that will move the needle.
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-6 py-20" style={{ backgroundColor: '#f5f5f5' }}>
        <div className="text-center mb-16">
          <h2 className="text-3xl font-medium text-black">Built for modern product teams</h2>
          <p className="mt-4 max-w-2xl mx-auto" style={{ color: '#434343' }}>
            Everything you need to transform scattered feedback into clear, actionable priorities
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          <Feature
            title="Universal inbox"
            desc="Aggregate feedback from support tickets, customer calls, team channels, and user research into a single source of truth."
          />
          <Feature
            title="Intelligent scoring"
            desc="Machine learning analyzes each piece of feedback for sentiment, urgency, and potential impact on your product and business."
          />
          <Feature
            title="Smart deduplication"
            desc="Automatically groups similar feedback together, so you see patterns instead of repetition and noise."
          />
          <Feature
            title="Priority rankings"
            desc="See what deserves attention now versus later. Filter by score, source, or team to surface the signal from the noise."
          />
          <Feature
            title="Weekly digests"
            desc="Get a curated summary every week highlighting top themes, urgent issues, and opportunities you shouldn't miss."
          />
          <Feature
            title="Export anywhere"
            desc="Push prioritized feedback directly to Linear, Jira, Notion, or your tool of choice to keep your workflow intact."
          />
        </div>
      </section>

      {/* How it works */}
      <section className="border-t bg-white" style={{ borderColor: '#e5e5e5' }}>
        <div className="mx-auto max-w-5xl px-6 py-20">
          <h2 className="text-3xl font-medium text-center mb-16 text-black">How it works</h2>
          <ol className="grid md:grid-cols-3 gap-12">
            <Step 
              n={1} 
              title="Capture" 
              desc="Forward emails, paste Slack threads, or connect integrations. FEED ingests feedback from any source in seconds." 
            />
            <Step 
              n={2} 
              title="Analyze" 
              desc="Our system automatically scores sentiment, urgency, and impact while detecting duplicate themes across all feedback." 
            />
            <Step 
              n={3} 
              title="Prioritize" 
              desc="Review your priority queue daily. Get weekly reports. Make confident decisions about what to build next." 
            />
          </ol>
        </div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-5xl px-6 py-20" style={{ backgroundColor: '#f5f5f5' }}>
        <div className="grid md:grid-cols-3 gap-12 text-center">
          <Stat value="10x" label="Faster feedback triage" />
          <Stat value="Zero" label="Important issues missed" />
          <Stat value="100%" label="Team alignment" />
        </div>
      </section>

      {/* CTA */}
      <section className="border-t text-white" style={{ borderColor: '#e5e5e5', backgroundColor: '#000000' }}>
        <div className="mx-auto max-w-5xl px-6 py-20 text-center">
          <h2 className="text-3xl md:text-4xl font-medium">Ready to ship what matters?</h2>
          <p className="mt-4 text-lg max-w-2xl mx-auto" style={{ color: '#b0b0b0' }}>
            Start organizing your feedback in minutes. No credit card required.
          </p>
          <div className="mt-8">
            <Link
              href="/feed"
              className="px-6 py-3 rounded-md bg-white text-sm font-medium hover:opacity-90 transition-opacity inline-block"
              style={{ color: '#000000' }}
            >
              Get Started
            </Link>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="mx-auto max-w-5xl px-6 py-20 bg-white">
        <h2 className="text-3xl font-medium mb-12 text-black">Frequently asked questions</h2>
        <div className="grid md:grid-cols-2 gap-x-12 gap-y-10">
          <QA 
            q="Where is my data stored?" 
            a="In your own Supabase Postgres instance. You maintain full ownership and control. FEED never has access to your raw feedback data." 
          />
          <QA 
            q="Can I import existing feedback?" 
            a="Yes. Import from CSV files or connect existing tools through our API. Historical context helps improve prioritization accuracy." 
          />
          <QA 
            q="Does this replace my project management tool?" 
            a="No. FEED identifies what deserves attention. You decide what to build and track work in Linear, Jira, or your preferred tool." 
          />
          <QA 
            q="How accurate is the scoring?" 
            a="The system learns from your decisions over time. Initial accuracy is strong, and it improves as you mark items as resolved or dismissed." 
          />
          <QA 
            q="What integrations are available?" 
            a="Currently supporting Slack, email forwarding, and manual entry. API access for custom integrations. More native integrations coming soon." 
          />
          <QA 
            q="How do I deploy this?" 
            a="Next.js frontend on Vercel, FastAPI backend anywhere, and Supabase for managed Postgres. Full deployment guide in documentation." 
          />
        </div>
      </section>
    </main>
  );
}

function Feature({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-lg p-8 bg-white border hover:shadow-sm transition-shadow" style={{ borderColor: '#e5e5e5' }}>
      <h3 className="font-medium text-lg text-black">{title}</h3>
      <p className="mt-3 text-sm leading-relaxed" style={{ color: '#434343' }}>{desc}</p>
    </div>
  );
}

function Step({ n, title, desc }: { n: number; title: string; desc: string }) {
  return (
    <li className="relative">
      <div className="flex flex-col items-center text-center">
        <div className="flex-shrink-0 w-12 h-12 rounded-full border-2 flex items-center justify-center font-medium text-lg mb-4" style={{ borderColor: '#000000', color: '#000000' }}>
          {n}
        </div>
        <div className="font-medium text-lg mb-2 text-black">{title}</div>
        <div className="text-sm leading-relaxed" style={{ color: '#434343' }}>{desc}</div>
      </div>
    </li>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-4xl font-medium text-black">{value}</div>
      <div className="mt-2" style={{ color: '#434343' }}>{label}</div>
    </div>
  );
}

function QA({ q, a }: { q: string; a: string }) {
  return (
    <div>
      <div className="font-medium text-base text-black">{q}</div>
      <div className="mt-2 text-sm leading-relaxed" style={{ color: '#434343' }}>{a}</div>
    </div>
  );
}

