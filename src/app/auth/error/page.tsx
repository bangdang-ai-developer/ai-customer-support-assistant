'use client';

import React from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { 
  AlertTriangle, 
  Home,
  RefreshCw,
  Sparkles 
} from 'lucide-react';

export default function AuthErrorPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get('error');

  const getErrorInfo = (error: string | null) => {
    switch (error) {
      case 'Configuration':
        return {
          title: 'Server Configuration Error',
          description: 'There is a problem with the server configuration.',
          suggestion: 'Please contact support if this error persists.'
        };
      case 'AccessDenied':
        return {
          title: 'Access Denied',
          description: 'You do not have permission to sign in.',
          suggestion: 'Please contact an administrator for access.'
        };
      case 'Verification':
        return {
          title: 'Unable to Verify',
          description: 'The verification link may have expired or already been used.',
          suggestion: 'Please try signing in again to get a new verification link.'
        };
      case 'Default':
      default:
        return {
          title: 'Authentication Error',
          description: 'An error occurred during the authentication process.',
          suggestion: 'Please try signing in again. If the problem persists, contact support.'
        };
    }
  };

  const errorInfo = getErrorInfo(error);

  const handleRetry = () => {
    window.location.href = '/auth/signin';
  };

  return (
    <div className="min-h-screen enhanced-chat-container flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-orange-600 flex items-center justify-center">
              <AlertTriangle className="w-7 h-7 text-white" />
            </div>
            <div className="absolute top-4 right-4">
              <ThemeToggle />
            </div>
          </div>
          <h1 className="text-2xl font-bold">Authentication Error</h1>
          <p className="text-muted-foreground">
            Something went wrong during sign in
          </p>
        </div>

        <Card className="glass card-lift">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-destructive" />
              {errorInfo.title}
            </CardTitle>
            <CardDescription>
              Error Code: {error || 'Unknown'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <AlertDescription>
                {errorInfo.description}
              </AlertDescription>
            </Alert>

            <p className="text-sm text-muted-foreground">
              {errorInfo.suggestion}
            </p>

            <div className="flex gap-2">
              <Button 
                onClick={handleRetry}
                className="flex-1 btn-glow"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
              
              <Button 
                variant="outline" 
                asChild
                className="flex-1"
              >
                <Link href="/">
                  <Home className="w-4 h-4 mr-2" />
                  Go Home
                </Link>
              </Button>
            </div>

            {/* Debug Info (only in development) */}
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-4 p-3 bg-muted rounded text-xs">
                <strong>Debug Info:</strong><br />
                Error: {error || 'No error code'}<br />
                URL: {window.location.href}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Help Links */}
        <div className="text-center space-y-2">
          <p className="text-xs text-muted-foreground">
            Need help? Contact support or try these options:
          </p>
          <div className="flex justify-center gap-4 text-xs">
            <Link 
              href="/auth/signin" 
              className="text-primary hover:underline"
            >
              Sign In
            </Link>
            <span className="text-muted-foreground">•</span>
            <Link 
              href="/" 
              className="text-primary hover:underline"
            >
              Continue as Guest
            </Link>
            <span className="text-muted-foreground">•</span>
            <Link 
              href="/demo" 
              className="text-primary hover:underline"
            >
              Try Demo
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}