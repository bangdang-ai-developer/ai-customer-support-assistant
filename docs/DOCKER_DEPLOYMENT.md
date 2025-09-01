# 🐳 Docker Deployment Guide

Complete Docker deployment guide for the BIWOCO AI Customer Support Assistant with support for both development and production environments.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Development Deployment](#-development-deployment)
- [Production Deployment](#-production-deployment)
- [Architecture Overview](#-architecture-overview)
- [Environment Configuration](#-environment-configuration)
- [Scaling & Load Balancing](#-scaling--load-balancing)
- [Monitoring & Logging](#-monitoring--logging)
- [Troubleshooting](#-troubleshooting)
- [Security Considerations](#-security-considerations)

## ⚡ Quick Start

### Development (Fastest)
```bash
# Clone and navigate to project
git clone <repo-url>
cd ai-customer-support-assistant

# Start with Docker
./docker-deploy.sh -e development -b -d

# Access at http://localhost:3000
```

### Production
```bash
# Configure environment
cp .env.docker .env
# Edit .env with your production settings

# Deploy to production
./docker-deploy.sh -e production -b -d --scale-backend 3 --scale-frontend 2
```

## 🔧 Prerequisites

### System Requirements
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **RAM**: 8GB minimum (16GB recommended for production)
- **CPU**: 4 cores minimum (8+ for production)
- **Disk**: 20GB available space
- **Network**: Ports 80, 443, 3000, 8000, 5432, 6379

### Install Docker (Ubuntu/Debian)
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

## 🏠 Development Deployment

Perfect for local development, testing, and debugging.

### Features
- **Hot Reload**: Automatic code reloading
- **Debug Mode**: Detailed logging and error messages
- **Port Exposure**: All services accessible on localhost
- **Volume Mounts**: Code changes reflect immediately

### Quick Start
```bash
# Option 1: Use deployment script (recommended)
./docker-deploy.sh -e development

# Option 2: Direct docker-compose
docker-compose up --build

# Option 3: Detached mode
./docker-deploy.sh -e development -b -d
```

### Services Started
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Next.js React application |
| **Backend** | http://localhost:8000 | FastAPI server + docs |
| **Database** | localhost:5432 | PostgreSQL database |
| **Redis** | localhost:6379 | Cache & sessions |
| **Nginx** | http://localhost:80 | Load balancer & proxy |

### Development Commands
```bash
# View logs
./docker-deploy.sh -c logs

# Restart services
./docker-deploy.sh -c restart

# Stop services
./docker-deploy.sh -c down

# Service status
./docker-deploy.sh -c status

# Rebuild and restart
./docker-deploy.sh -e development -b
```

## 🏢 Production Deployment

Enterprise-ready deployment with security, scaling, and monitoring.

### Features
- **SSL/TLS Termination**: HTTPS with custom certificates
- **Load Balancing**: Multiple backend/frontend instances
- **Security Headers**: Comprehensive security configuration
- **Health Checks**: Automatic service monitoring
- **Resource Limits**: Memory and CPU constraints
- **Auto-restart**: Automatic failure recovery

### Pre-Production Checklist

#### 1. **Environment Configuration**
```bash
# Copy production environment template
cp .env.docker .env

# Edit with production values
nano .env
```

#### 2. **SSL Certificates**
```bash
# Create SSL directory
mkdir -p docker/nginx/ssl

# Add your certificates
cp your-cert.pem docker/nginx/ssl/cert.pem
cp your-key.pem docker/nginx/ssl/key.pem

# Or use Let's Encrypt
# TODO: Add Let's Encrypt integration script
```

#### 3. **Security Settings**
```bash
# Generate secure secrets
node generate-secrets.js

# Update .env with generated secrets
# - NEXTAUTH_SECRET (64+ characters)
# - BACKEND_SECRET_KEY (64+ characters)  
# - POSTGRES_PASSWORD (strong password)
# - REDIS_PASSWORD (strong password)
```

### Production Deployment
```bash
# Standard deployment
./docker-deploy.sh -e production -b -d

# High-availability deployment
./docker-deploy.sh -e production -b -d \
  --scale-backend 5 \
  --scale-frontend 3

# With monitoring
ENABLE_MONITORING=true ./docker-deploy.sh -e production -b -d
```

### Production Services
| Service | Internal Port | External Access | Replicas |
|---------|---------------|----------------|----------|
| **Nginx** | 80, 443 | Public | 1 |
| **Frontend** | 3000 | Via Nginx | 2-5 |
| **Backend** | 8000 | Via Nginx | 3-10 |
| **Database** | 5432 | Internal only | 1 |
| **Redis** | 6379 | Internal only | 1 |
| **Worker** | - | Internal only | 2-5 |

## 🏗️ Architecture Overview

### Development Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    HOST SYSTEM                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │   Nginx     │ │  Frontend   │ │    Backend      │   │
│  │    :80      │ │    :3000    │ │     :8000       │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
│  ┌─────────────┐ ┌─────────────────────────────────┐   │
│  │ PostgreSQL  │ │            Redis                │   │
│  │   :5432     │ │            :6379                │   │
│  └─────────────┘ └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Production Architecture
```
                    ┌─────────────────┐
                    │      Nginx      │
                    │   Load Balancer │
                    │   SSL Termination│
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   Frontend      │
                    │   (2-5 replicas)│
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   Backend API   │
                    │   (3-10 replicas)│
                    └─────────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
  ┌─────▼─────┐        ┌─────▼─────┐        ┌─────▼─────┐
  │PostgreSQL │        │   Redis   │        │  Workers  │
  │ Database  │        │   Cache   │        │Background │
  │           │        │ Sessions  │        │   Jobs    │
  └───────────┘        └───────────┘        └───────────┘
```

## ⚙️ Environment Configuration

### Development (.env.local)
```bash
# NextAuth Configuration
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="dev-secret-32-chars-minimum"

# API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000"
NEXT_PUBLIC_WS_URL="ws://localhost:8000"

# AI Services
GOOGLE_AI_API_KEY="your-google-ai-api-key"
OPENAI_API_KEY="your-openai-api-key"
```

### Production (.env)
```bash
# Application
DOMAIN=your-domain.com
VERSION=latest
FRONTEND_URL=https://your-domain.com
WEBSOCKET_URL=wss://your-domain.com

# Database
POSTGRES_DB=biwoco_chatbot
POSTGRES_USER=biwoco_user
POSTGRES_PASSWORD=super-secure-password-64-chars

# Security Secrets (64+ characters each)
NEXTAUTH_SECRET=your-production-nextauth-secret-64-chars-minimum
BACKEND_SECRET_KEY=your-production-backend-secret-64-chars-minimum
REDIS_PASSWORD=your-redis-password-32-chars-minimum

# AI Services
GOOGLE_AI_API_KEY=your-production-google-ai-key
OPENAI_API_KEY=your-production-openai-key
PINECONE_API_KEY=your-production-pinecone-key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
GRAFANA_PASSWORD=your-grafana-admin-password

# Performance
LOG_LEVEL=INFO
RATE_LIMIT_MAX=1000
```

## 📈 Scaling & Load Balancing

### Horizontal Scaling
```bash
# Scale backend to 5 instances
./docker-deploy.sh -e production --scale-backend 5

# Scale both frontend and backend
./docker-deploy.sh -e production \
  --scale-frontend 3 \
  --scale-backend 7
```

### Resource Limits
Production containers have resource limits:

| Service | Memory Limit | CPU Limit | Memory Reserve | CPU Reserve |
|---------|--------------|-----------|----------------|-------------|
| Frontend | 1GB | 0.5 | 512MB | 0.25 |
| Backend | 2GB | 1.0 | 1GB | 0.5 |
| Database | 1GB | 0.5 | 512MB | 0.25 |
| Redis | 512MB | 0.25 | 256MB | 0.1 |

### Load Balancing Strategy
- **Frontend**: Round-robin load balancing
- **Backend**: Least connections with health checks
- **WebSockets**: Sticky sessions for real-time features
- **Static Files**: Aggressive caching with 1-year expiry

## 📊 Monitoring & Logging

### Built-in Health Checks
All services include health checks:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds  
- **Retries**: 3 attempts
- **Start Period**: 10-30 seconds

### Monitoring Stack (Optional)
Enable with `ENABLE_MONITORING=true`:

```bash
# Start with monitoring
ENABLE_MONITORING=true ./docker-deploy.sh -e production -b -d
```

**Services Added**:
- **Prometheus**: Metrics collection (localhost:9090)
- **Grafana**: Dashboards (localhost:3001)
- **Pre-configured Dashboards**: System & application metrics

### Log Management
```bash
# View all logs
./docker-deploy.sh -c logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs backend

# Follow logs in real-time
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# Log files location
ls -la logs/
```

### Log Rotation
Production logs are rotated automatically:
- **Max Size**: 100MB per file
- **Max Files**: 10 files per service
- **Compression**: Automatic gzip compression

## 🔧 Troubleshooting

### Common Issues

#### **Container Won't Start**
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs service-name

# Inspect container configuration
docker inspect container-name
```

#### **Database Connection Issues**
```bash
# Test database connection
docker exec -it biwoco-postgres-prod pg_isready -U biwoco_user

# Connect to database
docker exec -it biwoco-postgres-prod psql -U biwoco_user -d biwoco_chatbot

# Check database logs
docker-compose logs postgres
```

#### **Redis Connection Issues**
```bash
# Test Redis connection
docker exec -it biwoco-redis-prod redis-cli -a your-redis-password ping

# Monitor Redis
docker exec -it biwoco-redis-prod redis-cli -a your-redis-password monitor
```

#### **SSL/HTTPS Issues**
```bash
# Check SSL certificate
openssl x509 -in docker/nginx/ssl/cert.pem -text -noout

# Test SSL configuration
curl -I https://your-domain.com

# Check nginx configuration
docker exec -it biwoco-nginx-prod nginx -t
```

#### **High Memory Usage**
```bash
# Monitor container resources
docker stats

# Check container resource limits
docker inspect container-name | grep -A 10 Memory

# Scale down if needed
./docker-deploy.sh -e production --scale-backend 2
```

### Debugging Commands
```bash
# Shell into container
docker exec -it container-name /bin/bash

# View container processes
docker exec container-name ps aux

# Check network connectivity
docker network ls
docker network inspect biwoco-prod-network

# View environment variables
docker exec container-name env
```

## 🔒 Security Considerations

### Production Security Checklist

#### **✅ Secrets Management**
- [ ] Generate unique secrets for production
- [ ] Use strong passwords (64+ characters)
- [ ] Store secrets in environment variables only
- [ ] Never commit secrets to version control
- [ ] Rotate secrets regularly (every 90 days)

#### **✅ Network Security**
- [ ] Use HTTPS only in production
- [ ] Configure proper SSL certificates
- [ ] Enable security headers (HSTS, CSP, etc.)
- [ ] Implement rate limiting
- [ ] Restrict database/Redis access to internal network

#### **✅ Container Security**
- [ ] Run containers as non-root users
- [ ] Use minimal base images (Alpine Linux)
- [ ] Keep images updated
- [ ] Scan images for vulnerabilities
- [ ] Set resource limits

#### **✅ Application Security**
- [ ] Enable authentication for all endpoints
- [ ] Implement proper CORS settings
- [ ] Use secure session configuration
- [ ] Enable request size limits
- [ ] Configure proper error handling

### Security Commands
```bash
# Scan images for vulnerabilities (if docker scan available)
docker scan biwoco/frontend:latest
docker scan biwoco/backend:latest

# Check container security
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image biwoco/backend:latest

# Update all images
docker-compose pull
./docker-deploy.sh -e production -b
```

## 🚀 Deployment Automation

### CI/CD Integration

#### **GitHub Actions Example**
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        env:
          DOCKER_HOST: ssh://user@your-server
        run: |
          ./docker-deploy.sh -e production -b -d \
            --scale-backend 5 --scale-frontend 3
```

### Backup Strategy
```bash
# Database backup
docker exec biwoco-postgres-prod pg_dump -U biwoco_user biwoco_chatbot > backup.sql

# Redis backup
docker exec biwoco-redis-prod redis-cli -a password --rdb /data/dump.rdb

# Full application backup
tar -czf biwoco-backup-$(date +%Y%m%d).tar.gz \
  logs/ uploads/ docker/nginx/ssl/ .env
```

### Update Procedure
```bash
# 1. Backup current deployment
./docker-deploy.sh -c down
cp .env .env.backup

# 2. Pull latest code
git pull origin main

# 3. Rebuild and deploy
./docker-deploy.sh -e production -b -d

# 4. Verify deployment
curl -f https://your-domain.com/health
```

## 📞 Support

### Getting Help
1. **Check logs first**: `./docker-deploy.sh -c logs`
2. **Verify configuration**: Check `.env` file settings
3. **Test connectivity**: Use health check endpoints
4. **Resource monitoring**: Check `docker stats`
5. **Community support**: Create GitHub issue with logs

### Useful Resources
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)
- [PostgreSQL Docker Guide](https://hub.docker.com/_/postgres)

---

## 🎉 Success!

Once deployed successfully, you'll have:

✅ **Containerized Application**: All services running in Docker  
✅ **Load Balanced**: Multiple instances for high availability  
✅ **SSL Secured**: HTTPS encryption for production  
✅ **Health Monitoring**: Automatic health checks and restarts  
✅ **Scalable Architecture**: Easy horizontal scaling  
✅ **Production Ready**: Enterprise-grade security and performance  

**Your BIWOCO AI Assistant is now running on Docker!** 🐳🚀