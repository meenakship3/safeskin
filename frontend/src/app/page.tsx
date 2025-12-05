"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Header from "@/components/header"
import Footer from "@/components/footer"
import { Link as LinkIcon, Loader2 } from "lucide-react"

export default function HomePage() {
  const [nykaaUrl, setNykaaUrl] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  async function handleUrlSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!nykaaUrl.trim()) return

    setIsProcessing(true)
    setError(null)

    try {
      // Extract product ID from Nykaa URL
      // Example URL: https://www.nykaa.com/product-name/p/12345
      const match = nykaaUrl.match(/\/p\/(\d+)/)

      if (!match) {
        throw new Error("Invalid Nykaa URL. Please make sure it's a product link.")
      }

      const nykaaProductId = match[1]

      // Search for the product by nykaa_product_id
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/products/search?q=${nykaaProductId}&limit=1`
      )

      if (!response.ok) {
        throw new Error("Failed to search for product")
      }

      const results = await response.json()

      if (results.length === 0) {
        setError("Product not found in our database. Try searching by product name instead.")
        setIsProcessing(false)
        return
      }

      // Redirect to product page
      router.push(`/product/${results[0].id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process URL")
      setIsProcessing(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container mx-auto flex-1 px-4 py-8 sm:py-12 max-w-4xl">
        <div className="flex flex-col gap-6 sm:gap-8">
          {/* How It Works Section */}
          <div className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm sm:p-8">
            <h2 className="mb-6 text-center text-xl font-medium sm:mb-8 sm:text-2xl">How It Works</h2>
            <div className="grid gap-6 sm:gap-8 md:grid-cols-3">
              {[1, 2, 3].map((n) => (
                <div key={n} className="flex flex-col items-center gap-3 text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-base font-medium text-amber-800 sm:h-14 sm:w-14 sm:text-lg">
                    {n}
                  </div>
                  <h3 className="text-base font-medium sm:text-lg">
                    {n === 1 ? "Search" : n === 2 ? "Analyze" : "Results"}
                  </h3>
                  <p className="text-sm text-[#666] sm:text-base">
                    {n === 1
                      ? "Search by name in the bar above or paste a Nykaa link below"
                      : n === 2
                        ? "We check the ingredients against our comedogenic database"
                        : "Get instant feedback on product safety for acne-prone skin"}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Paste Nykaa Link Section */}
          <div className="rounded-xl border border-amber-300 bg-gradient-to-br from-amber-50 to-orange-50 p-6 sm:p-8">
            <div className="mb-4 flex items-center gap-2">
              <LinkIcon className="h-5 w-5 text-amber-700" />
              <h3 className="text-base font-medium text-amber-900 sm:text-lg">
                Have a Nykaa Link?
              </h3>
            </div>
            <p className="mb-4 text-sm text-amber-900/80 sm:text-base">
              Paste the product URL from Nykaa and we&apos;ll analyze it for you instantly.
            </p>
            <form onSubmit={handleUrlSubmit} className="space-y-3">
              <input
                type="url"
                placeholder="https://www.nykaa.com/product-name/p/12345"
                value={nykaaUrl}
                onChange={(e) => {
                  setNykaaUrl(e.target.value)
                  setError(null)
                }}
                className="w-full rounded-lg border border-amber-300 bg-white px-4 py-3 text-base outline-none transition focus:border-amber-500 focus:ring-2 focus:ring-amber-200"
                disabled={isProcessing}
              />
              {error && (
                <p className="text-sm text-red-600">{error}</p>
              )}
              <button
                type="submit"
                disabled={isProcessing || !nykaaUrl.trim()}
                className="w-full rounded-lg bg-amber-600 px-4 py-3 text-base font-medium text-white transition hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
              >
                {isProcessing ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analyzing...
                  </span>
                ) : (
                  "Analyze Product"
                )}
              </button>
            </form>
          </div>

          {/* Info Card */}
          <div className="rounded-xl border border-neutral-200 bg-neutral-50 p-6 sm:p-8">
            <h3 className="mb-3 text-base font-medium text-neutral-900 sm:text-lg">
              About SafeSkin
            </h3>
            <p className="mb-4 text-sm leading-relaxed text-neutral-700 sm:text-base">
              SafeSkin helps you identify potentially comedogenic (pore-clogging) ingredients in your skincare and makeup products. Our database contains over a thousand products and ingredients specifically checked for their comedogenic properties.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
