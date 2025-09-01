# Railway Deployment Guide for BIWOCO AI Assistant

## Overview
This guide will help you deploy the BIWOCO AI Customer Support Assistant to Railway cloud platform.

## Prerequisites
1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **API Keys**: Google AI API key for Gemini integration

## Backend Deployment (Step 1)

### 1. Create New Railway Project
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway new
```

### 2. Set Environment Variables
In Railway dashboard, add these environment variables:

```env
# Database (Railway will provide PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database

# Google AI (Required)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# NextAuth Configuration
NEXTAUTH_SECRET=your_production_secret_key_here
NEXTAUTH_URL=https://your-backend.railway.app

# API Configuration
API_V1_STR=/api/v1
HOST=0.0.0.0
PORT=$PORT

# Security
SECRET_KEY=your_jwt_secret_key_here
ALGORITHM=HS256

# CORS (Update with your frontend URL)
ALLOWED_HOSTS=["https://your-frontend.vercel.app", "https://your-backend.railway.app"]
```

### 3. Deploy Backend
```bash
# Connect to Railway project
railway link

# Deploy backend
railway up --detach
```

## Frontend Deployment (Step 2)

### 1. Deploy to Vercel (Recommended)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
vercel --prod
```

### 2. Set Frontend Environment Variables
In Vercel dashboard, add:

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app

# NextAuth Configuration  
NEXTAUTH_URL=https://your-frontend.vercel.app
NEXTAUTH_SECRET=your_production_secret_key_here

# Google AI
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

## Database Setup (Step 3)

### 1. Add PostgreSQL to Railway Project
```bash
# Add PostgreSQL service
railway add postgresql

# Get database URL
railway variables
```

### 2. Run Database Migrations
```bash
# Connect to your Railway backend
railway shell

# Run migrations
alembic upgrade head

# Create initial data (optional)
python -c "
from app.core.database import engine, Base
from app.models import user, conversation, knowledge, scenario, message
Base.metadata.create_all(bind=engine)
print('Database initialized successfully')
"
```

## Configuration Updates

### Update CORS Settings
Update `backend/app/core/config.py` with your production URLs:

```python
ALLOWED_HOSTS: List[str] = [
    "https://your-frontend.vercel.app",
    "https://your-backend.railway.app",
    "http://localhost:3000"  # Keep for local development
]
```

### Update Frontend API URLs
Update `.env.example` with production values:

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app
NEXTAUTH_URL=https://your-frontend.vercel.app
```

## Health Checks

### Backend Health Endpoint
Your backend includes a health check endpoint:
- URL: `https://your-backend.railway.app/health`
- Response: `{"status": "healthy", "service": "chatbot-api"}`

### API Documentation
Once deployed, access interactive API docs:
- Swagger UI: `https://your-backend.railway.app/docs`
- ReDoc: `https://your-backend.railway.app/redoc`

## Production Checklist

### Security
- [ ] Update NEXTAUTH_SECRET with strong production key
- [ ] Configure CORS with actual frontend URL
- [ ] Set secure JWT secret keys
- [ ] Enable HTTPS only in production

### Performance
- [ ] Enable caching for static assets
- [ ] Configure CDN for global performance
- [ ] Set up monitoring and logging
- [ ] Optimize database queries

### Features
- [ ] Upload business context documents for each scenario
- [ ] Test custom scenario creation
- [ ] Verify RAG functionality with real documents
- [ ] Test authentication with production URLs

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check database URL format
railway variables | grep DATABASE_URL

# Test database connection
railway shell
python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"
```

**CORS Errors**
- Ensure ALLOWED_HOSTS includes your frontend URL
- Check NEXTAUTH_URL matches your deployed frontend

**Environment Variables**
```bash
# List all variables
railway variables

# Set new variable
railway variables set KEY=value
```

## Scaling & Monitoring

### Railway Features
- **Auto-scaling**: Automatic scaling based on traffic
- **Monitoring**: Built-in metrics and logging
- **Custom Domains**: Connect your own domain
- **Environment Management**: Separate staging/production environments

### Recommended Settings
- **Memory**: 1GB minimum for ML dependencies
- **CPU**: 1 vCPU minimum for AI processing
- **Replicas**: 1-3 for high availability
- **Health Checks**: 30-second intervals

## Support
- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Community Support**: Railway Discord server
- **GitHub Issues**: Create issues in your repository

Your BIWOCO AI Assistant is now ready for production deployment on Railway! 🚀