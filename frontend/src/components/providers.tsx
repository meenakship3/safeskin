"use client"

import type { ReactNode } from "react"
import { ProductProvider } from "@/contexts/product-context"

export function Providers({ children }: { children: ReactNode }) {
  return <ProductProvider>{children}</ProductProvider>
}
