# 🔐 NextAuth.js NEXTAUTH_SECRET Setup Guide

This guide will help you properly configure the `NEXTAUTH_SECRET` key for the BIWOCO AI Customer Support Assistant.

## What is NEXTAUTH_SECRET?

The `NEXTAUTH_SECRET` is a **critical security key** used by NextAuth.js to:
- 🔐 **Sign JWT tokens** - Ensures token authenticity and prevents tampering
- 🍪 **Encrypt session cookies** - Secures user sessions in the browser
- 🛡️ **Protect against CSRF attacks** - Validates request authenticity
- 🔒 **Secure authentication flow** - Maintains session integrity

## ⚡ Quick Setup (Development)

### 1. Generate Your Secret Key

Choose one of these methods to generate a cryptographically secure secret:

**Option A: Using our built-in generator (Recommended)**
```bash
node generate-secrets.js
```

**Option B: Using OpenSSL (Unix/Mac/WSL)**
```bash
openssl rand -base64 32
```

**Option C: Using Node.js**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**Option D: Using Python**
```bash
python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

### 2. Create Environment File

Copy the example environment file:
```bash
cp .env.local.example .env.local
```

### 3. Add Your Secret

Edit `.env.local` and replace the NEXTAUTH_SECRET:
```bash
# Replace this with your generated secret
NEXTAUTH_SECRET="your-generated-secret-here"
```

### 4. Test the Setup

Start the development server:
```bash
npm run dev
```

Visit `http://localhost:3000` and try signing in with:
- **Demo User**: `demo@biwoco.com` / `demo123`
- **Admin User**: `admin@biwoco.com` / `admin123`
- **Guest Access**: Use "Continue as Guest" option

## 🏢 Production Setup

### Environment-Specific Secrets

**IMPORTANT**: Use different secrets for each environment!

```bash
# Development
NEXTAUTH_SECRET="dev-secret-32-chars-minimum-length"

# Staging  
NEXTAUTH_SECRET="staging-secret-different-from-dev"

# Production
NEXTAUTH_SECRET="production-secret-super-long-and-secure-64-chars-recommended"
```

### Deployment Checklist

- [ ] Generate unique secrets for each environment
- [ ] Use at least 32 characters (64+ recommended for production)
- [ ] Store secrets securely (never commit to git)
- [ ] Set up secret rotation schedule (every 90 days)
- [ ] Configure environment variables in your hosting platform

### Popular Hosting Platforms

**Vercel**
```bash
vercel env add NEXTAUTH_SECRET
# Paste your secret when prompted
```

**Netlify**
```bash
netlify env:set NEXTAUTH_SECRET "your-production-secret"
```

**Heroku**
```bash
heroku config:set NEXTAUTH_SECRET="your-production-secret"
```

**Railway**
```bash
railway variables set NEXTAUTH_SECRET="your-production-secret"
```

## 🔍 Security Best Practices

### ✅ DO
- **Use cryptographically secure random generation**
- **Use different secrets for each environment**
- **Make secrets at least 32 characters long**
- **Rotate secrets regularly (every 90 days)**
- **Store secrets in secure environment variables**
- **Use longer secrets (64+ chars) for production**

### ❌ DON'T
- **Never commit secrets to version control**
- **Don't use predictable or simple passwords**
- **Don't share secrets between environments**  
- **Don't hardcode secrets in your application**
- **Don't use the same secret across different applications**

## 🧪 Testing Your Setup

### 1. Verify Environment Variables

Create a test script to verify your setup:

```typescript
// test-auth.ts
console.log('NEXTAUTH_URL:', process.env.NEXTAUTH_URL)
console.log('NEXTAUTH_SECRET:', process.env.NEXTAUTH_SECRET ? '✅ Set' : '❌ Missing')
console.log('SECRET_LENGTH:', process.env.NEXTAUTH_SECRET?.length || 0)

if (!process.env.NEXTAUTH_SECRET) {
  console.error('❌ NEXTAUTH_SECRET is required!')
  process.exit(1)
}

if (process.env.NEXTAUTH_SECRET.length < 32) {
  console.warn('⚠️  NEXTAUTH_SECRET should be at least 32 characters')
}

console.log('✅ NextAuth configuration looks good!')
```

### 2. Test Authentication Flow

1. Start the application: `npm run dev`
2. Visit: `http://localhost:3000`
3. Click "Sign In" button
4. Try different authentication methods
5. Verify session persistence across page reloads

### 3. Check Browser Developer Tools

In browser dev tools (F12) → Application → Cookies:
- Look for `next-auth.session-token` cookie
- Should be `HttpOnly` and `Secure` (in production)
- Should not be readable by JavaScript

## 🔧 Troubleshooting

### Common Issues

**❌ "NEXTAUTH_SECRET is not set"**
```bash
# Make sure .env.local exists and contains NEXTAUTH_SECRET
cat .env.local | grep NEXTAUTH_SECRET
```

**❌ Authentication not working**
```bash
# Check if secret is too short
echo $NEXTAUTH_SECRET | wc -c
# Should be 32+ characters
```

**❌ Sessions not persisting**
```bash
# Verify NEXTAUTH_URL matches your domain
echo $NEXTAUTH_URL
# Should match exactly: http://localhost:3000 (dev) or https://yourdomain.com (prod)
```

**❌ CSRF errors**
```bash
# Usually indicates secret mismatch or missing
# Regenerate and restart your application
```

### Debug Mode

Enable NextAuth debug mode in development:

```bash
# Add to .env.local
NEXTAUTH_DEBUG=true
```

Then check console logs for detailed authentication flow information.

## 📱 Demo Accounts

For testing purposes, the following accounts are pre-configured:

| Role | Email | Password | Features |
|------|-------|----------|----------|
| **Demo User** | `demo@biwoco.com` | `demo123` | Standard chat access |
| **Admin** | `admin@biwoco.com` | `admin123` | Full admin dashboard |
| **Guest** | - | - | Anonymous chat access |

## 🚀 Advanced Configuration

### JWT Customization

```typescript
// In your auth config
jwt: {
  maxAge: 7 * 24 * 60 * 60, // 7 days
  // Optional: Custom JWT encoding
  encode: async ({ secret, token }) => {
    // Custom JWT encoding logic
  },
  decode: async ({ secret, token }) => {
    // Custom JWT decoding logic
  }
}
```

### Session Configuration

```typescript
session: {
  strategy: 'jwt',
  maxAge: 7 * 24 * 60 * 60, // 7 days
  updateAge: 24 * 60 * 60, // 24 hours
}
```

### Custom Cookie Settings

```typescript
cookies: {
  sessionToken: {
    name: `${process.env.NODE_ENV === 'production' ? '__Secure-' : ''}next-auth.session-token`,
    options: {
      httpOnly: true,
      sameSite: 'lax',
      path: '/',
      secure: process.env.NODE_ENV === 'production'
    }
  }
}
```

## 📚 Additional Resources

- [NextAuth.js Documentation](https://next-auth.js.org/)
- [JWT.io - Token Debugger](https://jwt.io/)
- [OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [Node.js Crypto Documentation](https://nodejs.org/api/crypto.html)

## 🆘 Support

If you encounter issues:

1. **Check this documentation** - Common solutions are covered above
2. **Review console logs** - Enable debug mode for detailed info
3. **Verify environment variables** - Use the test script provided
4. **Check GitHub Issues** - Search for similar problems
5. **Create an issue** - If problem persists, create a detailed issue report

---

## 🎉 Success!

Once configured correctly, you'll have:
- ✅ Secure JWT token signing
- ✅ Encrypted session cookies  
- ✅ CSRF protection
- ✅ Persistent user sessions
- ✅ Multiple authentication providers
- ✅ Role-based access control

**Your BIWOCO AI Assistant is now securely configured!** 🚀