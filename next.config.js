/** @type {import('next').NextConfig} */
const nextConfig = {
  // Optimize for development speed
  ...(process.env.NODE_ENV === 'production' ? { output: 'standalone' } : {}),
  
  // Network access configuration removed - not needed in Next.js 15
  
  images: {
    domains: ['localhost', '192.168.1.5'],
  },
  
  // Speed up development builds
  typescript: {
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },
  
  eslint: {
    ignoreDuringBuilds: process.env.NODE_ENV === 'development',
  },
  
  env: {
    DATABASE_URL: process.env.DATABASE_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    GOOGLE_AI_API_KEY: process.env.GOOGLE_AI_API_KEY,
    PINECONE_API_KEY: process.env.PINECONE_API_KEY,
    PINECONE_ENVIRONMENT: process.env.PINECONE_ENVIRONMENT,
    REDIS_URL: process.env.REDIS_URL,
  },
}

module.exports = nextConfig