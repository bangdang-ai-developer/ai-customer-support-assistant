# Environment Variables Reference

## 🔧 **Production Environment Variables**

### **Railway PostgreSQL Database**
```env
# Get this from Railway dashboard after creating PostgreSQL service
DATABASE_URL=postgresql://postgres:password@containers-us-west-xxx.railway.app:7432/railway
```

### **Render Backend Service**
Set these in Render dashboard:

```env
# Database Connection (from Railway)
DATABASE_URL=postgresql://postgres:password@containers-us-west-xxx.railway.app:7432/railway

# Google AI Integration (Required)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Authentication & Security
NEXTAUTH_SECRET=your_long_random_secret_32_chars_minimum
SECRET_KEY=your_jwt_secret_key_here
NEXTAUTH_URL=https://your-frontend.vercel.app

# CORS Configuration
ALLOWED_HOSTS=["https://your-frontend.vercel.app", "*"]

# Server Configuration
HOST=0.0.0.0
PORT=$PORT
```

### **Vercel Frontend Service**
Set these in Vercel dashboard:

```env
# Backend API Connection
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_WS_URL=wss://your-backend.onrender.com

# Authentication
NEXTAUTH_URL=https://your-frontend.vercel.app
NEXTAUTH_SECRET=your_long_random_secret_32_chars_minimum

# Google AI (for any client-side features)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

## 🔑 **How to Generate Secure Keys**

### **NEXTAUTH_SECRET & SECRET_KEY**
```bash
# Generate secure random key (32+ characters)
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Or use OpenSSL
openssl rand -base64 32

# Or use Python
python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

### **Google AI API Key**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create new API key
3. Copy the key (starts with "AIza...")

## 🌐 **URL Format Examples**

### **Frontend URLs (Vercel)**
```
Production: https://biwoco-ai-assistant.vercel.app
Preview: https://biwoco-ai-assistant-git-main.vercel.app
```

### **Backend URLs (Render)**
```
Production: https://biwoco-ai-backend.onrender.com
Health Check: https://biwoco-ai-backend.onrender.com/health
API Docs: https://biwoco-ai-backend.onrender.com/docs
```

### **Database URLs (Railway)**
```
Format: postgresql://postgres:password@host:port/database
Example: postgresql://postgres:abc123@containers-us-west-123.railway.app:7432/railway
```

## ✅ **Environment Variable Checklist**

### **Before Deployment:**
- [ ] Generated secure NEXTAUTH_SECRET (32+ chars)
- [ ] Generated secure SECRET_KEY (32+ chars)  
- [ ] Obtained Google AI API key
- [ ] Created Railway PostgreSQL database
- [ ] Noted all URLs and credentials

### **After Deployment:**
- [ ] Updated NEXTAUTH_URL with actual Vercel URL
- [ ] Updated NEXT_PUBLIC_API_URL with actual Render URL
- [ ] Updated ALLOWED_HOSTS with actual frontend URL
- [ ] Tested all services connect properly

## 🚨 **Security Notes**

- **Never commit** environment variables to Git
- **Use different keys** for different environments
- **Rotate keys** periodically (every 90 days)
- **Limit CORS** to your actual frontend domain in production
- **Monitor** for any unusual activity

Your environment variables are now ready for **secure, production deployment**! 🔐