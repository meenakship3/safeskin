import type React from "react"
import type { Metadata } from "next"
import "./globals.css"
import { Providers } from "@/components/providers"

export const metadata: Metadata = {
  title: "safeskin",
  description: "Check if skincare products may cause acne",
    generator: 'v0.app'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#f9f7f4] text-[#333] antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
