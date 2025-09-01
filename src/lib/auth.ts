/**
 * NextAuth.js configuration for BIWOCO AI Assistant
 * Handles authentication and session management
 */

import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
import { JWT } from 'next-auth/jwt'

declare module 'next-auth' {
  interface Session {
    user: {
      id: string
      name?: string | null
      email?: string | null
      image?: string | null
      role?: string
    }
  }

  interface User {
    id: string
    role?: string
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id: string
    role?: string
  }
}

export const authOptions: NextAuthOptions = {
  // Configure authentication providers
  providers: [
    // Google OAuth Provider
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID ?? '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? '',
    }),

    // GitHub OAuth Provider  
    GitHubProvider({
      clientId: process.env.GITHUB_ID ?? '',
      clientSecret: process.env.GITHUB_SECRET ?? '',
    }),

    // Credentials Provider for demo purposes
    CredentialsProvider({
      id: 'credentials',
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        // Demo authentication - replace with real authentication logic
        if (credentials?.email === 'demo@biwoco.com' && credentials?.password === 'demo123') {
          return {
            id: 'demo-user',
            name: 'Demo User',
            email: 'demo@biwoco.com',
            role: 'user'
          }
        }
        
        if (credentials?.email === 'admin@biwoco.com' && credentials?.password === 'admin123') {
          return {
            id: 'admin-user', 
            name: 'Admin User',
            email: 'admin@biwoco.com',
            role: 'admin'
          }
        }

        // In production, validate against your user database
        // const user = await validateUserCredentials(credentials.email, credentials.password)
        // return user ? { id: user.id, name: user.name, email: user.email, role: user.role } : null

        return null
      }
    }),

    // Guest Provider for anonymous access
    CredentialsProvider({
      id: 'guest',
      name: 'Continue as Guest',
      credentials: {},
      async authorize() {
        // Generate anonymous user for demo
        const guestId = `guest-${Date.now()}-${Math.random().toString(36).substring(2, 15)}`
        return {
          id: guestId,
          name: 'Guest User',
          email: `${guestId}@guest.demo`,
          role: 'guest'
        }
      }
    })
  ],

  // Configure session strategy
  session: {
    strategy: 'jwt',
    maxAge: 7 * 24 * 60 * 60, // 7 days
  },

  // JWT configuration
  jwt: {
    maxAge: 7 * 24 * 60 * 60, // 7 days
    // Secret is automatically read from NEXTAUTH_SECRET environment variable
  },

  // Callback functions
  callbacks: {
    async jwt({ token, user, account }) {
      // Persist user data in the token
      if (user) {
        token.id = user.id
        token.role = user.role
      }
      
      // Handle OAuth account linking
      if (account) {
        token.accessToken = account.access_token
        token.provider = account.provider
      }

      return token
    },

    async session({ session, token }) {
      // Send properties to the client
      if (session.user) {
        session.user.id = token.id
        session.user.role = token.role
      }
      return session
    },

    async redirect({ url, baseUrl }) {
      // Allows relative callback URLs
      if (url.startsWith("/")) return `${baseUrl}${url}`
      // Allows callback URLs on the same origin
      else if (new URL(url).origin === baseUrl) return url;
      return baseUrl;
    }
  },

  // Custom pages
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
    verifyRequest: '/auth/verify',
  },

  // Events for logging and analytics
  events: {
    async signIn({ user, account, profile, isNewUser }) {
      // Log to your analytics service
    },
    async signOut({ token }) {
      // Handle sign out
    },
    async createUser({ user }) {
      // Send welcome email, create user record, etc.
    }
  },

  // Disable debug for better performance
  debug: false,

  // Security configuration
  cookies: {
    sessionToken: {
      name: `${process.env.NODE_ENV === 'production' ? '__Secure-' : ''}next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production'
      }
    },
    callbackUrl: {
      name: `${process.env.NODE_ENV === 'production' ? '__Secure-' : ''}next-auth.callback-url`,
      options: {
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production'
      }
    },
    csrfToken: {
      name: `${process.env.NODE_ENV === 'production' ? '__Host-' : ''}next-auth.csrf-token`,
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production'
      }
    }
  }
}

export default authOptions