'use client';

import React, { useState, useEffect } from 'react';
import { signIn, getProviders, getCsrfToken } from 'next-auth/react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Sparkles, 
  Mail, 
  Lock, 
  Github, 
  Chrome,
  User,
  AlertCircle
} from 'lucide-react';

interface Provider {
  id: string;
  name: string;
  type: string;
  signinUrl: string;
  callbackUrl: string;
}

export default function SignInPage() {
  const [providers, setProviders] = useState<Record<string, Provider> | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [csrfToken, setCsrfToken] = useState('');
  
  const searchParams = useSearchParams();
  const error = searchParams.get('error');
  const callbackUrl = searchParams.get('callbackUrl') || '/';

  useEffect(() => {
    (async () => {
      const res = await getProviders();
      const token = await getCsrfToken();
      setProviders(res);
      setCsrfToken(token || '');
    })();
  }, []);

  const handleCredentialsSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await signIn('credentials', {
        email,
        password,
        callbackUrl,
        redirect: false,
      });

      if (result?.error) {
        console.error('Sign in error:', result.error);
      } else if (result?.ok) {
        const baseUrl = `${window.location.protocol}//${window.location.host}`;
        const redirectUrl = callbackUrl || baseUrl + '/';
        window.location.replace(redirectUrl);
      }
    } catch (error) {
      console.error('Sign in failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGuestSignIn = async () => {
    setLoading(true);
    try {
      await signIn('guest', {
        callbackUrl,
        redirect: true,
      });
    } catch (error) {
      console.error('Guest sign in failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getErrorMessage = (error: string) => {
    switch (error) {
      case 'CredentialsSignin':
        return 'Invalid email or password. Try demo@biwoco.com / demo123';
      case 'OAuthAccountNotLinked':
        return 'Account already exists with different provider';
      case 'OAuthCreateAccount':
        return 'Could not create account';
      case 'EmailCreateAccount':
        return 'Could not create account';
      case 'Callback':
        return 'Error in callback';
      case 'OAuthCallback':
        return 'Error in OAuth callback';
      case 'EmailSignin':
        return 'Check your email for sign in link';
      case 'SessionRequired':
        return 'Please sign in to access this page';
      default:
        return 'An error occurred during sign in';
    }
  };

  return (
    <div className="min-h-screen enhanced-chat-container flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-2xl font-bold gradient-text">Welcome Back</h1>
          <p className="text-muted-foreground">
            Sign in to BIWOCO AI Assistant
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="animate-slide-in">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {getErrorMessage(error)}
            </AlertDescription>
          </Alert>
        )}

        <Card className="glass card-lift">
          <CardHeader className="space-y-1">
            <CardTitle className="text-xl">Sign In</CardTitle>
            <CardDescription>
              Choose your preferred sign in method
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* OAuth Providers */}
            <div className="space-y-2">
              {providers && providers.google && (
                <Button
                  variant="outline"
                  className="w-full btn-glow"
                  onClick={() => signIn('google', { callbackUrl })}
                  disabled={loading}
                >
                  <Chrome className="w-4 h-4 mr-2" />
                  Continue with Google
                </Button>
              )}

              {providers && providers.github && (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => signIn('github', { callbackUrl })}
                  disabled={loading}
                >
                  <Github className="w-4 h-4 mr-2" />
                  Continue with GitHub
                </Button>
              )}
            </div>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>

            {/* Credentials Form */}
            <form onSubmit={handleCredentialsSignIn} className="space-y-4">
              <input name="csrfToken" type="hidden" defaultValue={csrfToken} />
              
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="demo@biwoco.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 focus-ring"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="demo123"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 focus-ring"
                    required
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full btn-glow"
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            {/* Demo Accounts */}
            <div className="space-y-2 text-xs text-center text-muted-foreground">
              <p>Demo accounts:</p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-muted/50 p-2 rounded">
                  <strong>User:</strong><br />
                  demo@biwoco.com<br />
                  demo123
                </div>
                <div className="bg-muted/50 p-2 rounded">
                  <strong>Admin:</strong><br />
                  admin@biwoco.com<br />
                  admin123
                </div>
              </div>
            </div>

            {/* Guest Access */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or
                </span>
              </div>
            </div>

            <Button
              variant="ghost"
              className="w-full quick-action"
              onClick={handleGuestSignIn}
              disabled={loading}
            >
              <User className="w-4 h-4 mr-2" />
              Continue as Guest
            </Button>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}