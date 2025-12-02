import Link from "next/link"
import Header from "@/components/header"
import Footer from "@/components/footer"
import { Check, X } from "lucide-react"

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container mx-auto flex-1 px-4 py-4 sm:py-8 max-w-5xl">
        <div className="flex flex-col gap-6 sm:gap-8">
          <div className="grid gap-4 sm:gap-6 md:grid-cols-2 md:gap-8">
            <div className="flex flex-col items-center gap-3 rounded-xl border border-green-200 bg-white p-4 text-center shadow-sm sm:gap-4 sm:p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100 sm:h-16 sm:w-16">
                <Check className="h-6 w-6 text-green-600 sm:h-8 sm:w-8" />
              </div>
              <h2 className="text-lg font-medium sm:text-xl">Safe Products</h2>
              <p className="max-w-[36ch] text-sm text-[#666] sm:max-w-none sm:text-base">
                {"Products that don't contain ingredients known to cause acne or irritation"}
              </p>
              <Link
                href="/safe"
                className="inline-flex items-center justify-center rounded-md border border-green-200 px-4 py-2 text-xs font-medium text-green-700 transition hover:bg-green-50 hover:text-green-800 sm:text-sm"
              >
                View Examples
              </Link>
            </div>

            <div className="flex flex-col items-center gap-3 rounded-xl border border-red-200 bg-white p-4 text-center shadow-sm sm:gap-4 sm:p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 sm:h-16 sm:w-16">
                <X className="h-6 w-6 text-red-600 sm:h-8 sm:w-8" />
              </div>
              <h2 className="text-lg font-medium sm:text-xl">Unsafe Products</h2>
              <p className="max-w-[36ch] text-sm text-[#666] sm:max-w-none sm:text-base">
                Products that contain ingredients that may cause acne or irritation
              </p>
              <Link
                href="/unsafe"
                className="inline-flex items-center justify-center rounded-md border border-red-200 px-4 py-2 text-xs font-medium text-red-700 transition hover:bg-red-50 hover:text-red-800 sm:text-sm"
              >
                View Examples
              </Link>
            </div>
          </div>

          <div className="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm sm:p-6">
            <h2 className="mb-3 text-lg font-medium sm:mb-4 sm:text-xl">How It Works</h2>
            <div className="grid gap-4 sm:gap-6 md:grid-cols-3">
              {[1, 2, 3].map((n) => (
                <div key={n} className="flex flex-col items-center gap-2 text-center">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100 text-sm font-medium text-amber-800 sm:h-10 sm:w-10 sm:text-base">
                    {n}
                  </div>
                  <h3 className="text-sm font-medium sm:text-base">
                    {n === 1 ? "Search" : n === 2 ? "Analyze" : "Results"}
                  </h3>
                  <p className="text-xs text-[#666] sm:text-sm">
                    {n === 1
                      ? "Enter your product name in the search bar"
                      : n === 2
                        ? "We check the ingredients against our database"
                        : "Get instant feedback on product safety"}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
