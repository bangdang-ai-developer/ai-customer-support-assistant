import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { ThemeProvider } from "@/contexts/ThemeContext"
import "../globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Sign In - BIWOCO AI Assistant",
  description: "Sign in to BIWOCO AI Customer Support Assistant",
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className={inter.className}>
      <ThemeProvider>
        {children}
      </ThemeProvider>
    </div>
  )
}
