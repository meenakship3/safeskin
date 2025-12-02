"use client"

import Link from "next/link"
import Header from "@/components/header"
import Footer from "@/components/footer"
import { X } from "lucide-react"

export default function UnsafeProductPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="container mx-auto flex-1 px-4 py-4 sm:py-8 max-w-5xl">
        <div className="mx-auto max-w-2xl">
          <div className="flex flex-col items-center gap-4 rounded-xl border border-red-200 bg-white p-4 text-center shadow-sm sm:gap-6 sm:p-8">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 sm:h-20 sm:w-20">
              <X className="h-8 w-8 text-red-600 sm:h-10 sm:w-10" />
            </div>

            <div className="space-y-2">
              <h2 className="text-xl font-medium text-red-800 sm:text-2xl">This product may cause acne</h2>
              <p className="text-sm text-[#666] sm:text-base">
                {"We've checked the ingredient list and found some acne causing ingredients."}
              </p>
            </div>

            <div className="w-full border-t border-red-100 pt-4 sm:pt-6">
              <h3 className="mb-2 text-left text-sm font-medium sm:text-base">Problematic Ingredients</h3>
              <div className="rounded-lg bg-red-50 p-3 text-xs text-red-800 sm:p-4 sm:text-sm">
                <ul className="list-inside list-disc space-y-1">
                  <li>Isopropyl Myristate (Comedogenic Rating: 5/5)</li>
                  <li>Coconut Oil (Comedogenic Rating: 4/5)</li>
                  <li>Sodium Lauryl Sulfate (Potential Irritant)</li>
                </ul>
              </div>
            </div>

            <div className="w-full space-y-3 text-left sm:space-y-4">
              <h3 className="text-sm font-medium sm:text-base">Recommendations</h3>
              <ul className="list-inside list-disc text-xs text-[#666] sm:text-sm">
                <li>Consider alternatives without these ingredients</li>
                <li>If you use this product, monitor your skin&apos;s reaction</li>
                <li>Consult with a dermatologist if you have concerns</li>
              </ul>
            </div>

            <div className="w-full rounded-lg bg-neutral-50 p-3 text-xs text-[#666] sm:p-4">
              Disclaimer: This is not intended to replace dermatological advice. Patch test before using the product.
            </div>
          </div>

          <div className="mt-4 text-center sm:mt-6">
            <Link
              href="/"
              className="inline-flex items-center justify-center rounded-md border border-amber-300 px-4 py-2 text-sm font-medium text-amber-800 transition hover:bg-amber-50"
            >
              Search Another Product
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
