"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Header from "@/components/header"
import Footer from "@/components/footer"
import { Loader2, ChevronLeft, ChevronRight } from "lucide-react"
import Link from "next/link"

interface ProductSearchResult {
  id: number
  nykaa_product_id: string
  name: string
  category: string
  image_url: string
  relevance: number
}

interface PaginatedSearchResponse {
  results: ProductSearchResult[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
}

export default function SearchPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const query = searchParams.get("q") || ""
  const currentPage = parseInt(searchParams.get("page") || "1")

  const [searchResults, setSearchResults] = useState<PaginatedSearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!query || query.length < 2) {
      router.push("/")
      return
    }

    async function fetchResults() {
      setIsLoading(true)
      setError(null)

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/products/search/paginated?q=${encodeURIComponent(
            query
          )}&page=${currentPage}&page_size=20`
        )

        if (!response.ok) {
          throw new Error("Search failed")
        }

        const data = await response.json()
        setSearchResults(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to search products")
      } finally {
        setIsLoading(false)
      }
    }

    fetchResults()
  }, [query, currentPage, router])

  function handlePageChange(newPage: number) {
    const params = new URLSearchParams()
    params.set("q", query)
    params.set("page", newPage.toString())
    router.push(`/search?${params.toString()}`)
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container mx-auto flex-1 px-4 py-8 max-w-4xl">
        <div className="mb-6">
          <h1 className="text-2xl font-medium text-neutral-900 sm:text-3xl">
            Search Results for &quot;{query}&quot;
          </h1>
          {searchResults && (
            <p className="mt-2 text-sm text-neutral-600 sm:text-base">
              Found {searchResults.total_count} product{searchResults.total_count !== 1 ? "s" : ""}
            </p>
          )}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center gap-2 py-12 text-neutral-600">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Searching...</span>
          </div>
        ) : error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-600">
            {error}
          </div>
        ) : searchResults && searchResults.results.length === 0 ? (
          <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-8 text-center">
            <p className="text-neutral-600">No products found for &quot;{query}&quot;</p>
            <p className="mt-2 text-sm text-neutral-500">
              Try searching with a different term or check your spelling
            </p>
          </div>
        ) : (
          <>
            {/* Results Grid */}
            <div className="grid gap-4 sm:grid-cols-2">
              {searchResults?.results.map((product) => (
                <Link
                  key={product.id}
                  href={`/product/${product.id}`}
                  className="group rounded-lg border border-neutral-200 bg-white p-4 transition hover:border-amber-300 hover:shadow-md"
                >
                  <div className="flex gap-4">
                    {product.image_url && (
                      <img
                        src={product.image_url}
                        alt={product.name}
                        className="h-20 w-20 flex-shrink-0 rounded object-cover"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-neutral-900 line-clamp-2 group-hover:text-amber-800">
                        {product.name}
                      </h3>
                      <p className="mt-1 text-sm text-neutral-600">{product.category}</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {searchResults && searchResults.total_pages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="flex h-10 w-10 items-center justify-center rounded-lg border border-neutral-200 bg-white text-neutral-700 transition hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-40"
                  aria-label="Previous page"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>

                <div className="flex gap-1">
                  {Array.from({ length: searchResults.total_pages }, (_, i) => i + 1)
                    .filter((page) => {
                      // Show first, last, current, and adjacent pages
                      return (
                        page === 1 ||
                        page === searchResults.total_pages ||
                        Math.abs(page - currentPage) <= 1
                      )
                    })
                    .map((page, idx, arr) => {
                      // Add ellipsis
                      const showEllipsisBefore = idx > 0 && page - arr[idx - 1] > 1
                      return (
                        <div key={page} className="flex items-center gap-1">
                          {showEllipsisBefore && (
                            <span className="px-2 text-neutral-400">...</span>
                          )}
                          <button
                            onClick={() => handlePageChange(page)}
                            className={`flex h-10 w-10 items-center justify-center rounded-lg border transition ${
                              currentPage === page
                                ? "border-amber-500 bg-amber-50 font-medium text-amber-800"
                                : "border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
                            }`}
                          >
                            {page}
                          </button>
                        </div>
                      )
                    })}
                </div>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === searchResults.total_pages}
                  className="flex h-10 w-10 items-center justify-center rounded-lg border border-neutral-200 bg-white text-neutral-700 transition hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-40"
                  aria-label="Next page"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            )}

            {/* Page info */}
            {searchResults && searchResults.total_pages > 1 && (
              <p className="mt-4 text-center text-sm text-neutral-500">
                Page {currentPage} of {searchResults.total_pages}
              </p>
            )}
          </>
        )}
      </main>

      <Footer />
    </div>
  )
}
