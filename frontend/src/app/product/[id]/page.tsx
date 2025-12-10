"use client"

import { useEffect } from "react"
import { useParams } from "next/navigation"
import Header from "@/components/header"
import Footer from "@/components/footer"
import { useProduct } from "@/contexts/product-context"
import { Check, X, AlertCircle, ExternalLink } from "lucide-react"

export default function ProductResultPage() {
  const params = useParams<{ id: string }>()
  const { getProductById, currentProduct, isLoadingProduct, productError } = useProduct()

  useEffect(() => {
    if (params?.id) {
      const productId = parseInt(params.id, 10)
      if (!isNaN(productId)) {
        getProductById(productId)
      }
    }
  }, [params?.id, getProductById])

  const handleCheckAnother = () => {
    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: "smooth" })
    // Focus the search input and ensure cursor is visible
    setTimeout(() => {
      const searchInput = document.querySelector('input[type="search"]') as HTMLInputElement
      if (searchInput) {
        searchInput.focus()
        searchInput.click() // Ensures cursor appears on mobile
      }
    }, 500) // Wait for smooth scroll to complete
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="container mx-auto flex-1 max-w-3xl px-4 py-4 sm:py-8">
        {isLoadingProduct ? (
          <div className="py-8 text-center text-[#666]">Loading product information...</div>
        ) : productError ? (
          <div className="rounded-xl border border-red-200 bg-white p-4 text-center shadow-sm sm:p-8">
            <div className="flex h-16 w-16 mx-auto items-center justify-center rounded-full bg-red-100 sm:h-20 sm:w-20">
              <X className="h-8 w-8 text-red-600 sm:h-10 sm:w-10" />
            </div>
            <h2 className="mt-4 text-xl font-medium text-red-800 sm:text-2xl">Error</h2>
            <p className="mt-2 text-sm text-[#666] sm:text-base">{productError}</p>
            <div className="mt-6">
              <button
                onClick={handleCheckAnother}
                className="inline-flex items-center justify-center rounded-md border border-amber-300 px-4 py-2 text-sm font-medium text-amber-800 transition hover:bg-amber-50"
              >
                Back to Search
              </button>
            </div>
          </div>
        ) : !currentProduct ? (
          <div className="py-8 text-center text-[#666]">No product found</div>
        ) : currentProduct.safety_status === "unknown" ? (
          <>
            <div className="rounded-xl border border-amber-200 bg-white p-6 shadow-sm sm:p-8">
              {/* Product Header with Image */}
              <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:gap-6">
                {currentProduct.image_url && (
                  <img
                    src={currentProduct.image_url}
                    alt={currentProduct.name}
                    className="h-32 w-32 flex-shrink-0 rounded-lg object-cover sm:h-40 sm:w-40"
                  />
                )}
                <div className="flex-1 text-center sm:text-left">
                  <h1 className="text-2xl font-medium text-[#333] sm:text-3xl">{currentProduct.name}</h1>
                  <p className="mt-2 text-base text-[#666] sm:text-lg">{currentProduct.category}</p>
                  {currentProduct.url && (
                    <a
                      href={currentProduct.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 inline-flex items-center gap-1.5 text-sm text-amber-700 hover:text-amber-800 sm:text-base"
                    >
                      View on Nykaa <ExternalLink className="h-4 w-4" />
                    </a>
                  )}
                </div>
              </div>

              {/* Status Badge */}
              <div className="mt-6 flex items-center justify-center gap-3 rounded-lg bg-amber-50 p-4">
                <AlertCircle className="h-6 w-6 text-amber-600" />
                <p className="text-base font-medium text-amber-800 sm:text-lg">
                  Ingredients Not Available
                </p>
              </div>

              <p className="mt-4 text-center text-sm text-[#666] sm:text-base">
                Please check the product packaging or manufacturer&apos;s website for ingredient information.
              </p>
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={handleCheckAnother}
                className="inline-flex items-center justify-center rounded-lg border border-amber-300 bg-white px-6 py-3 text-base font-medium text-amber-800 transition hover:bg-amber-50"
              >
                Check Another Product
              </button>
            </div>
          </>
        ) : currentProduct.safety_status === "safe" ? (
          <>
            <div className="rounded-xl border border-green-200 bg-white p-6 shadow-sm sm:p-8">
              {/* Product Header with Image */}
              <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:gap-6">
                {currentProduct.image_url && (
                  <img
                    src={currentProduct.image_url}
                    alt={currentProduct.name}
                    className="h-32 w-32 flex-shrink-0 rounded-lg object-cover sm:h-40 sm:w-40"
                  />
                )}
                <div className="flex-1 text-center sm:text-left">
                  <h1 className="text-2xl font-medium text-[#333] sm:text-3xl">{currentProduct.name}</h1>
                  <p className="mt-2 text-base text-[#666] sm:text-lg">{currentProduct.category}</p>
                  {currentProduct.url && (
                    <a
                      href={currentProduct.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 inline-flex items-center gap-1.5 text-sm text-green-700 hover:text-green-800 sm:text-base"
                    >
                      View on Nykaa <ExternalLink className="h-4 w-4" />
                    </a>
                  )}
                </div>
              </div>

              {/* Status Badge */}
              <div className="mt-6 flex items-center justify-center gap-3 rounded-lg bg-green-50 p-4 sm:p-5">
                <Check className="h-6 w-6 flex-shrink-0 text-green-600 sm:h-7 sm:w-7" />
                <div className="text-left">
                  <p className="text-lg font-medium text-green-800 sm:text-xl">Safe to use!</p>
                  <p className="mt-0.5 text-sm text-green-700 sm:text-base">
                    No acne-causing ingredients found
                  </p>
                </div>
              </div>
            </div>
            <p className="mt-6 text-center text-xs text-[#888] sm:text-sm">
                Disclaimer: This is not intended to replace dermatological advice. Patch test before using the product.
            </p>

            <div className="mt-6 text-center">
              <button
                onClick={handleCheckAnother}
                className="inline-flex items-center justify-center rounded-lg border border-amber-300 bg-white px-6 py-3 text-base font-medium text-amber-800 transition hover:bg-amber-50"
              >
                Check Another Product
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="rounded-xl border border-red-200 bg-white p-6 shadow-sm sm:p-8">
              {/* Product Header with Image */}
              <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:gap-6">
                {currentProduct.image_url && (
                  <img
                    src={currentProduct.image_url}
                    alt={currentProduct.name}
                    className="h-32 w-32 flex-shrink-0 rounded-lg object-cover sm:h-40 sm:w-40"
                  />
                )}
                <div className="flex-1 text-center sm:text-left">
                  <h1 className="text-2xl font-medium text-[#333] sm:text-3xl">{currentProduct.name}</h1>
                  <p className="mt-2 text-base text-[#666] sm:text-lg">{currentProduct.category}</p>
                  {currentProduct.url && (
                    <a
                      href={currentProduct.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 inline-flex items-center gap-1.5 text-sm text-red-700 hover:text-red-800 sm:text-base"
                    >
                      View on Nykaa <ExternalLink className="h-4 w-4" />
                    </a>
                  )}
                </div>
              </div>

              {/* Status Badge */}
              <div className="mt-6 flex items-center justify-center gap-3 rounded-lg bg-red-50 p-4 sm:p-5">
                <X className="h-6 w-6 flex-shrink-0 text-red-600 sm:h-7 sm:w-7" />
                <div className="text-left">
                  <p className="text-lg font-medium text-red-800 sm:text-xl">May cause acne</p>
                  <p className="mt-0.5 text-sm text-red-700 sm:text-base">
                    {currentProduct.comedogenic_count} problematic {currentProduct.comedogenic_count === 1 ? "ingredient" : "ingredients"} found
                  </p>
                </div>
              </div>

              {/* Problematic Ingredients */}
              <div className="mt-6">
                <h2 className="mb-3 text-center text-base font-medium text-[#333] sm:text-lg">
                  Ingredients to avoid:
                </h2>
                <div className="flex flex-wrap justify-center gap-2">
                  {currentProduct.comedogenic_ingredients.map((ing, i) => (
                    <span
                      key={i}
                      className="rounded-full bg-red-100 px-4 py-2 text-sm font-medium text-red-800 sm:text-base"
                    >
                      {ing}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <p className="mt-6 text-center text-xs text-[#888] sm:text-sm">
                Disclaimer: This is not intended to replace dermatological advice. Patch test before using the product.
            </p>

            <div className="mt-6 text-center">
              <button
                onClick={handleCheckAnother}
                className="inline-flex items-center justify-center rounded-lg border border-amber-300 bg-white px-6 py-3 text-base font-medium text-amber-800 transition hover:bg-amber-50"
              >
                Check Another Product
              </button>
            </div>
          </>
        )}
      </main>
      <Footer />
    </div>
  )
}
