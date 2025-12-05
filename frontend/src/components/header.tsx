"use client"

import Link from "next/link"
import { Leaf } from "lucide-react"
import SearchBar from "@/components/search-bar"

export default function Header() {
  return (
    <header className="border-b border-amber-100/50 bg-[#f9f7f4] px-4 py-4 sm:py-6">
      <div className="mx-auto flex max-w-[42rem] flex-col items-center gap-4">
        {/* Logo + Tagline Group (tighter spacing) */}
        <div className="flex flex-col items-center gap-1.5">
          <Link href="/" className="flex items-center justify-center gap-2">
            <Leaf className="h-6 w-6 text-amber-800 sm:h-7 sm:w-7 md:h-8 md:w-8" />
            <h1 className="font-serif text-3xl font-normal tracking-tight text-amber-800 sm:text-4xl md:text-5xl">
              safeskin
            </h1>
          </Link>
          <p className="px-2 text-center text-sm font-light text-[#666] sm:max-w-md sm:text-base">
            Check if your favorite products are acne-safe
          </p>
        </div>

        <SearchBar />
      </div>
    </header>
  )
}
