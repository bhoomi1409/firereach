import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'FireReach — Autonomous Outreach Engine',
  description: 'AI-powered autonomous outreach. Signal → Research → Send.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#080C14] text-slate-100 antialiased min-h-screen`}>
        {children}
      </body>
    </html>
  )
}