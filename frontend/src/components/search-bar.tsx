"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { useProduct } from "@/contexts/product-context"
import { Search, Loader2 } from "lucide-react"

export default function SearchBar() {
  const [query, setQuery] = useState("")
  const [showResults, setShowResults] = useState(false)
  const { searchProducts, searchResults, isSearching, searchError, clearSearch } = useProduct()
  const router = useRouter()
  const searchRef = useRef<HTMLDivElement>(null)

  // Search as user types (debounced)
  useEffect(() => {
    if (query.length < 2) {
      clearSearch()
      setShowResults(false)
      return
    }

    const timeoutId = setTimeout(() => {
      searchProducts(query)
      setShowResults(true)
    }, 300) // 300ms debounce

    return () => clearTimeout(timeoutId)
  }, [query])

  // Close results when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  function handleProductClick(productId: number) {
    setShowResults(false)
    setQuery("")
    clearSearch()
    router.push(`/product/${productId}`)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    // Navigate to search results page if query is valid
    if (query.length >= 2) {
      setShowResults(false)
      router.push(`/search?q=${encodeURIComponent(query)}`)
    }
  }

  return (
    <div ref={searchRef} className="w-full max-w-sm px-4 sm:max-w-md sm:px-0">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <input
            type="search"
            placeholder="Search for a product"
            aria-label="Search for a product"
            className="w-full rounded-full border border-amber-200 bg-white px-4 py-3 pr-12 text-base outline-none ring-0 transition placeholder:text-[#888] focus:border-amber-400 focus:ring-2 focus:ring-amber-200 sm:py-6"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => {
              if (searchResults.length > 0) setShowResults(true)
            }}
          />
          <button
            type="submit"
            aria-label="Search"
            className="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full text-amber-800 transition hover:bg-amber-100 hover:text-amber-900 sm:h-10 sm:w-10"
            disabled={isSearching}
          >
            {isSearching ? (
              <Loader2 className="h-4 w-4 animate-spin sm:h-5 sm:w-5" />
            ) : (
              <Search className="h-4 w-4 sm:h-5 sm:w-5" />
            )}
          </button>

          {/* Search Results Dropdown */}
          {showResults && query.length >= 2 && (
            <div className="absolute left-0 right-0 top-full z-50 mt-2 max-h-[70vh] overflow-y-auto rounded-lg border border-amber-200 bg-white shadow-lg">
              {isSearching ? (
                <div className="flex items-center justify-center gap-2 p-4 text-base text-[#666]">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Searching...
                </div>
              ) : searchError ? (
                <div className="p-4 text-base text-red-600">
                  {searchError}
                </div>
              ) : searchResults.length === 0 ? (
                <div className="p-4 text-base text-[#666]">
                  No products found for "{query}"
                </div>
              ) : (
                <>
                  <ul className="divide-y divide-amber-100">
                    {searchResults.slice(0, 5).map((product) => (
                      <li key={product.id}>
                        <button
                          type="button"
                          onClick={() => handleProductClick(product.id)}
                          className="w-full px-4 py-3 text-left transition hover:bg-amber-50 active:bg-amber-100"
                        >
                          <div className="flex items-start gap-3">
                            {product.image_url && (
                              <img
                                src={product.image_url}
                                alt={product.name}
                                className="h-12 w-12 flex-shrink-0 rounded object-cover"
                              />
                            )}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-[#333] truncate">
                                {product.name}
                              </p>
                              <p className="text-xs text-[#888] mt-0.5">
                                {product.category}
                              </p>
                            </div>
                          </div>
                        </button>
                      </li>
                    ))}
                  </ul>
                  {searchResults.length > 0 && (
                    <div className="border-t border-amber-100 p-3">
                      <button
                        type="submit"
                        className="w-full rounded-lg bg-amber-50 px-4 py-2 text-center text-sm font-medium text-amber-800 transition hover:bg-amber-100"
                      >
                        View All Results ({searchResults.length}+)
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </form>
    </div>
  )
}
