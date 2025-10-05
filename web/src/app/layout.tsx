import type { Metadata } from "next";
import { Geist, Geist_Mono, Playfair_Display } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const playfair = Playfair_Display({
  variable: "--font-display",
  subsets: ["latin"],
  style: ["normal", "italic"],
});

export const metadata: Metadata = {
  title: "FEED – Customer Feedback Prioritizer",
  description: "Capture, score, and prioritize customer feedback with clarity.",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} ${playfair.variable} antialiased bg-background text-foreground`}>
        <div className="min-h-dvh flex flex-col">
          <header className="border-b bg-white/70 backdrop-blur supports-[backdrop-filter]:bg-white/60">
            <div className="container mx-auto max-w-6xl px-6 h-14 flex items-center justify-between">
              <a href="/" className="flex items-center gap-2">
                <div className="size-6 rounded-md bg-black" />
                <span className="font-semibold tracking-tight">FEED</span>
              </a>
              <nav className="hidden sm:flex items-center gap-6 text-sm text-gray-700">
                <a className="hover:text-black" href="/">Home</a>
                <a className="hover:text-black" href="/feed">FEED</a>
                <a className="hover:text-black" href="#" target="_blank" rel="noopener noreferrer">GitHub</a>
              </nav>
            </div>
          </header>

          <main className="flex-1">{children}</main>

          <footer className="border-t bg-white">
            <div className="container mx-auto max-w-6xl px-6 py-4 text-xs text-gray-500 flex items-center justify-between">
              <span>© {new Date().getFullYear()} FEED</span>
              <span className="hidden sm:block">Built with Next.js + FastAPI</span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
