"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import SearchBar from "@/components/search-bar"

export default function Header() {
  const pathname = usePathname()

  return (
    <header className="bg-[#f9f7f4] px-4 py-4 sm:py-6">
      <div className="mx-auto flex max-w-[42rem] flex-col items-center gap-4">
        <Link href="/" className="flex items-center justify-center">
          <h1 className="font-serif text-3xl font-normal text-amber-800 sm:text-4xl md:text-5xl">safeskin</h1>
        </Link>
        <p className="px-2 text-center text-sm text-[#666] sm:max-w-md sm:text-base">
          Check if your skincare products contain ingredients that may cause acne or irritation
        </p>

        <nav className="flex gap-2 sm:gap-4">
          <Link
            href="/"
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition sm:px-4 sm:py-2 ${
              pathname === "/"
                ? "bg-amber-100 text-amber-900"
                : "text-amber-700 hover:bg-amber-50 hover:text-amber-900"
            }`}
          >
            Home
          </Link>
          <Link
            href="/safe"
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition sm:px-4 sm:py-2 ${
              pathname === "/safe"
                ? "bg-green-100 text-green-900"
                : "text-green-700 hover:bg-green-50 hover:text-green-900"
            }`}
          >
            Safe Products
          </Link>
          <Link
            href="/unsafe"
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition sm:px-4 sm:py-2 ${
              pathname === "/unsafe"
                ? "bg-red-100 text-red-900"
                : "text-red-700 hover:bg-red-50 hover:text-red-900"
            }`}
          >
            Unsafe Products
          </Link>
        </nav>

        <SearchBar />
      </div>
    </header>
  )
}
