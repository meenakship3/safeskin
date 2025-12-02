"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { useProduct } from "@/contexts/product-context"
import { Search } from "lucide-react"

export default function SearchBar() {
  const [query, setQuery] = useState("")
  const { searchProduct } = useProduct()
  const router = useRouter()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    const productId = searchProduct(query)
    router.push(`/product/${productId}`)
  }

  return (
    <div className="w-full max-w-sm px-4 sm:max-w-md sm:px-0">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <input
            type="search"
            placeholder="Search for a product"
            aria-label="Search for a product"
            className="w-full rounded-full border border-amber-200 bg-white px-4 py-3 pr-12 text-sm outline-none ring-0 transition placeholder:text-[#888] focus:border-amber-400 focus:ring-2 focus:ring-amber-200 sm:py-6 sm:text-base"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="submit"
            aria-label="Search"
            className="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full text-amber-800 transition hover:bg-amber-100 hover:text-amber-900 sm:h-10 sm:w-10"
          >
            <Search className="h-4 w-4 sm:h-5 sm:w-5" />
          </button>
        </div>
      </form>
    </div>
  )
}
