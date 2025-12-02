"use client"

import type React from "react"
import { createContext, useContext, useMemo, useState } from "react"

type Product = {
  id: string
  name: string
  isSafe: boolean
  analysis?: string
  benefits?: string[]
  problematicIngredients?: string[]
  recommendations?: string[]
}

type Ctx = {
  searchQuery: string
  setSearchQuery: (q: string) => void
  currentProduct: Product | null
  searchProduct: (q: string) => string
  getProduct: (id: string) => Product | null
}

const sampleProducts: Record<string, Product> = {
  "product-1": {
    id: "product-1",
    name: "Gentle Cleanser",
    isSafe: true,
    analysis:
      "All ingredients have been verified as non-comedogenic and unlikely to cause irritation for most skin types.",
    benefits: ["Suitable for acne-prone skin", "Non-comedogenic formula", "Free from common irritants"],
  },
  "product-2": {
    id: "product-2",
    name: "Moisturizing Cream",
    isSafe: false,
    problematicIngredients: [
      "Isopropyl Myristate (Comedogenic Rating: 5/5)",
      "Coconut Oil (Comedogenic Rating: 4/5)",
      "Sodium Lauryl Sulfate (Potential Irritant)",
    ],
    recommendations: [
      "Consider alternatives without these ingredients",
      "If you use this product, monitor your skin's reaction",
      "Consult with a dermatologist if you have concerns",
    ],
  },
}

const ProductContext = createContext<Ctx | null>(null)

export function ProductProvider({ children }: { children: React.ReactNode }) {
  const [searchQuery, setSearchQuery] = useState("")
  const [currentProduct, setCurrentProduct] = useState<Product | null>(null)

  function searchProduct(q: string) {
    setSearchQuery(q)
    const productId = q.toLowerCase().includes("gentle") ? "product-1" : "product-2"
    return productId
  }

  function getProduct(id: string) {
    const p = sampleProducts[id] ?? null
    setCurrentProduct(p)
    return p
  }

  const value = useMemo(
    () => ({ searchQuery, setSearchQuery, currentProduct, searchProduct, getProduct }),
    [searchQuery, currentProduct],
  )

  return <ProductContext.Provider value={value}>{children}</ProductContext.Provider>
}

export function useProduct() {
  const ctx = useContext(ProductContext)
  if (!ctx) throw new Error("useProduct must be used within ProductProvider")
  return ctx
}
