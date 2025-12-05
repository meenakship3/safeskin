"use client"

import type React from "react"
import { createContext, useContext, useMemo, useState } from "react"

// Backend API URL from environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Type definitions matching backend response models
type Ingredient = {
  name: string
  is_comedogenic: boolean
  position: number | null
}

type ProductSearchResult = {
  id: number
  nykaa_product_id: string
  name: string
  category: string
  image_url: string
  relevance: number
}

type ProductDetail = {
  id: number
  nykaa_product_id: string
  name: string
  category: string
  url: string
  image_url: string
  safety_status: "safe" | "unsafe" | "unknown"
  comedogenic_ingredients: string[]
  comedogenic_count: number
  all_ingredients: Ingredient[]
}

type Ctx = {
  searchQuery: string
  setSearchQuery: (q: string) => void
  searchResults: ProductSearchResult[]
  isSearching: boolean
  searchError: string | null
  currentProduct: ProductDetail | null
  isLoadingProduct: boolean
  productError: string | null
  searchProducts: (query: string) => Promise<void>
  getProductById: (id: number) => Promise<void>
  clearSearch: () => void
}

const ProductContext = createContext<Ctx | null>(null)

export function ProductProvider({ children }: { children: React.ReactNode }) {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<ProductSearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)

  const [currentProduct, setCurrentProduct] = useState<ProductDetail | null>(null)
  const [isLoadingProduct, setIsLoadingProduct] = useState(false)
  const [productError, setProductError] = useState<string | null>(null)

  async function searchProducts(query: string) {
    if (!query.trim() || query.length < 2) {
      setSearchResults([])
      return
    }

    setIsSearching(true)
    setSearchError(null)

    try {
      const response = await fetch(
        `${API_URL}/api/products/search?q=${encodeURIComponent(query)}&limit=20`
      )

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`)
      }

      const data: ProductSearchResult[] = await response.json()
      setSearchResults(data)
      setSearchQuery(query)
    } catch (error) {
      console.error("Search error:", error)
      setSearchError(error instanceof Error ? error.message : "Search failed")
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  async function getProductById(id: number) {
    setIsLoadingProduct(true)
    setProductError(null)
    setCurrentProduct(null)

    try {
      const response = await fetch(`${API_URL}/api/products/${id}`)

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Product not found")
        }
        throw new Error(`Failed to fetch product: ${response.statusText}`)
      }

      const data: ProductDetail = await response.json()
      setCurrentProduct(data)
    } catch (error) {
      console.error("Product fetch error:", error)
      setProductError(error instanceof Error ? error.message : "Failed to load product")
    } finally {
      setIsLoadingProduct(false)
    }
  }

  function clearSearch() {
    setSearchResults([])
    setSearchQuery("")
    setSearchError(null)
  }

  const value = useMemo(
    () => ({
      searchQuery,
      setSearchQuery,
      searchResults,
      isSearching,
      searchError,
      currentProduct,
      isLoadingProduct,
      productError,
      searchProducts,
      getProductById,
      clearSearch,
    }),
    [searchQuery, searchResults, isSearching, searchError, currentProduct, isLoadingProduct, productError]
  )

  return <ProductContext.Provider value={value}>{children}</ProductContext.Provider>
}

export function useProduct() {
  const ctx = useContext(ProductContext)
  if (!ctx) throw new Error("useProduct must be used within ProductProvider")
  return ctx
}
