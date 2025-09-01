import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { ThemeProvider } from '@/contexts/ThemeContext'

const inter = Inter({ subsets: ['latin'] })
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#8b5cf6' },
    { media: '(prefers-color-scheme: dark)', color: '#7c3aed' }
  ],
}

export const metadata: Metadata = {
  title: 'BIWOCO AI Customer Support Assistant',
  description: 'Multi-scenario AI-powered customer support chatbot demo with real-time capabilities',
  keywords: 'AI, chatbot, customer support, e-commerce, SaaS, service business',
  authors: [{ name: 'BIWOCO Team' }],


  openGraph: {
    title: 'BIWOCO AI Customer Support Assistant',
    description: 'Experience the future of customer support with our AI-powered assistant',
    type: 'website',
    locale: 'en_US',
    siteName: 'BIWOCO AI Assistant',
  },
  robots: {
    index: true,
    follow: true,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#8b5cf6' },
    { media: '(prefers-color-scheme: dark)', color: '#7c3aed' }
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
      </head>
      <body className={inter.className} suppressHydrationWarning>
        <ThemeProvider>
          <AuthProvider>
            <div id="root">
              {children}
            </div>
            <div id="portal-root"></div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}