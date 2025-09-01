# Free Deployment Guide - BIWOCO AI Assistant

## 🆓 **100% Free Deployment Stack**

### **Frontend: Vercel (Free)**
- **Next.js hosting** with global CDN
- **Custom domains** and automatic HTTPS
- **GitHub integration** with auto-deployments
- **Generous free tier** - perfect for demos

### **Backend: Render (Free)**
- **FastAPI hosting** with 512MB RAM
- **Automatic deployments** from GitHub
- **Free tier limitations**: Spins down after 15min inactivity

### **Database: Render PostgreSQL (Free - Same Platform)**
- **Included PostgreSQL** with Render backend
- **1GB storage** on free tier
- **Same platform** - simplified management
- **Always-on database** - doesn't sleep

## 🚀 **Step-by-Step Deployment (Simplified)**

### **Step 1: Deploy Backend + Database to Render**

1. **Push to GitHub** (if not already done)
```bash
git add .
git commit -m "🚀 BIWOCO AI Assistant - Production Ready"
git push origin main
```

2. **Create Render Account & Deploy**:
   - Sign up at [render.com](https://render.com)
   - Click "New Web Service"
   - Connect GitHub and select your repository
   - Configure deployment:

   **Build Settings:**
   ```bash
   Build Command: cd backend && pip install -r requirements.txt
   Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Add PostgreSQL Database**:
   - In Render dashboard, click "New PostgreSQL"
   - Choose free plan (1GB storage)
   - Copy the **External Database URL**

4. **Set Environment Variables** in Render Web Service:
```env
# Database (from Render PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/database

# Google AI Integration
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Authentication
NEXTAUTH_SECRET=your_long_random_secret_key_here
NEXTAUTH_URL=https://your-project.vercel.app

# Security & CORS
SECRET_KEY=your_jwt_secret_key_here
ALLOWED_HOSTS=["https://your-project.vercel.app", "*"]

# Server Configuration
HOST=0.0.0.0
```

### **Step 2: Deploy Frontend to Vercel**

1. **Deploy to Vercel**:
```bash
# Install Vercel CLI (if not already)
npm install -g vercel

# Deploy frontend
vercel login
vercel --prod
```

2. **Set Environment Variables** in Vercel Dashboard:
```env
NEXTAUTH_URL=https://your-project.vercel.app
NEXTAUTH_SECRET=your_long_random_secret_key_here
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_WS_URL=wss://your-backend.onrender.com
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

### **Step 3: Initialize Database**

Once backend is deployed, initialize your database:

1. **Use Render Shell** (in Render dashboard):
```bash
# Go to your web service → Shell tab
python -c "
from app.core.database import engine, Base
from app.models import user, conversation, knowledge, scenario, message
Base.metadata.create_all(bind=engine)
print('✅ Database tables created successfully')
"
```

2. **Verify Backend Health**:
   - Visit: `https://your-backend.onrender.com/health`
   - Should return: `{"status": "healthy", "service": "chatbot-api"}`

3. **Test API Documentation**:
   - Visit: `https://your-backend.onrender.com/docs`
   - Interactive API documentation should load

## 💰 **Cost Breakdown (100% Free)**

### **Render Free Tier:**
- ✅ **Web Service**: 512MB RAM, 750 hours/month
- ✅ **PostgreSQL**: 1GB storage, unlimited connections
- ✅ **Custom domains** and automatic SSL
- ⚠️ **Limitation**: Services sleep after 15 minutes of inactivity

### **Vercel Free Tier:**
- ✅ **Hosting**: Unlimited personal projects
- ✅ **Bandwidth**: 100GB/month (more than sufficient)
- ✅ **Global CDN** with excellent performance
- ✅ **Custom domains** and automatic HTTPS

## 🔧 **Production Optimizations**

### **Backend Performance (render.yaml):**
```yaml
services:
  - type: web
    name: biwoco-ai-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: "/health"
    
databases:
  - name: biwoco-postgres
    databaseName: biwoco_ai
    user: biwoco_user
    plan: free
```

### **Frontend Performance (vercel.json):**
```json
{
  "builds": [{"src": "package.json", "use": "@vercel/next"}],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-backend.onrender.com"
  }
}
```

## 🎯 **Why This Stack?**

### **Advantages:**
- ✅ **Single platform** for backend + database (Render)
- ✅ **Best-in-class frontend** hosting (Vercel)
- ✅ **Zero cost** for demo and assessment
- ✅ **Professional URLs** and SSL certificates
- ✅ **Automatic deployments** from GitHub
- ✅ **Production-ready** performance and reliability

### **Perfect for BIWOCO Assessment:**
- ✅ **Live demo** accessible worldwide
- ✅ **Professional presentation** with custom URLs
- ✅ **Scalable architecture** ready for production
- ✅ **Zero infrastructure costs** for evaluation period

## 🚀 **Deployment Timeline:**

- **Database setup**: 5 minutes on Render
- **Backend deployment**: 10-15 minutes (including build)
- **Frontend deployment**: 3-5 minutes on Vercel
- **Configuration**: 5 minutes for environment variables
- **Total**: 25-30 minutes to live demo!

Your **BIWOCO AI Customer Support Assistant** will be **globally accessible** for your technical assessment - completely free! 🎉