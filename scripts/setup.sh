#!/bin/bash

# BIWOCO AI Customer Support Assistant - Quick Setup Script
# This script sets up the development environment automatically

set -e

echo "🚀 Setting up BIWOCO AI Customer Support Assistant..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3.11+ is required but not installed."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 18+ is required but not installed."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed."
        exit 1
    fi
    
    # Check PostgreSQL (optional)
    if command -v psql &> /dev/null; then
        POSTGRES_VERSION=$(psql --version | awk '{print $3}')
        print_success "PostgreSQL $POSTGRES_VERSION found"
    else
        print_warning "PostgreSQL not found. You'll need to set up a database manually."
    fi
    
    # Check Redis (optional)
    if command -v redis-cli &> /dev/null; then
        print_success "Redis found"
    else
        print_warning "Redis not found. You'll need to set up Redis manually."
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up Python backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cp .env.example .env
        print_warning "Please edit backend/.env with your actual API keys and database URLs"
    fi
    
    cd ..
    print_success "Backend setup complete!"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up Next.js frontend..."
    
    # Install npm dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create .env.local if it doesn't exist
    if [ ! -f ".env.local" ]; then
        print_status "Creating frontend environment file..."
        print_status "Generating NEXTAUTH_SECRET..."
        
        # Generate NEXTAUTH_SECRET
        if command -v node &> /dev/null; then
            NEXTAUTH_SECRET=$(node -e "console.log(require('crypto').randomBytes(32).toString('base64'))")
        elif command -v openssl &> /dev/null; then
            NEXTAUTH_SECRET=$(openssl rand -base64 32)
        else
            NEXTAUTH_SECRET="please-generate-a-secure-32-character-secret-key"
            print_warning "Could not generate NEXTAUTH_SECRET automatically. Please generate manually."
        fi
        
        # Create .env.local with all required variables
        cat > .env.local << EOF
# NextAuth Configuration
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="$NEXTAUTH_SECRET"

# API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000"
NEXT_PUBLIC_WS_URL="ws://localhost:8000"

# AI Services (Add your API keys)
GOOGLE_AI_API_KEY=""

# Development Settings
NODE_ENV="development"
NEXT_PUBLIC_APP_NAME="BIWOCO AI Assistant"
EOF
        print_success "Frontend .env.local created with secure NEXTAUTH_SECRET"
        print_warning "Don't forget to add your GOOGLE_AI_API_KEY to .env.local"
    fi
    
    print_success "Frontend setup complete!"
}

# Setup database (optional)
setup_database() {
    print_status "Setting up database..."
    
    # Check if PostgreSQL is running
    if command -v pg_isready &> /dev/null && pg_isready -q; then
        print_success "PostgreSQL is running"
        
        # Create database if it doesn't exist
        createdb biwoco_chatbot 2>/dev/null || print_warning "Database might already exist"
        
        # Run migrations
        cd backend
        source venv/bin/activate
        if command -v alembic &> /dev/null; then
            print_status "Running database migrations..."
            alembic upgrade head
            print_success "Database migrations complete!"
        else
            print_warning "Alembic not found. Please run migrations manually."
        fi
        cd ..
    else
        print_warning "PostgreSQL not running. Please start PostgreSQL and create database manually."
    fi
}

# Create startup scripts
create_scripts() {
    print_status "Creating startup scripts..."
    
    # Backend startup script
    cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "Starting BIWOCO AI Backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF
    chmod +x start_backend.sh
    
    # Frontend startup script
    cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "Starting BIWOCO AI Frontend..."
npm run dev
EOF
    chmod +x start_frontend.sh
    
    # Combined startup script
    cat > start_all.sh << 'EOF'
#!/bin/bash
echo "Starting BIWOCO AI Customer Support Assistant..."
echo "=================================================="

# Function to handle cleanup
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "Starting backend..."
./start_backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "Starting frontend..."
./start_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "🎉 BIWOCO AI Assistant is now running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait
EOF
    chmod +x start_all.sh
    
    print_success "Startup scripts created!"
}

# Main setup function
main() {
    echo ""
    echo "🤖 BIWOCO AI Customer Support Assistant Setup"
    echo "============================================="
    echo ""
    
    check_requirements
    setup_backend
    setup_frontend
    setup_database
    create_scripts
    
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "Next steps:"
    echo "1. Edit backend/.env with your API keys (Google AI, etc.)"
    echo "2. Add GOOGLE_AI_API_KEY to .env.local for AI features"
    echo "3. Ensure PostgreSQL and Redis are running"
    echo "4. Validate your setup: node validate-auth.js"
    echo "5. Run: ./start_all.sh"
    echo ""
    echo "Or start services individually:"
    echo "- Backend: ./start_backend.sh"
    echo "- Frontend: ./start_frontend.sh"
    echo ""
    echo "Access your application:"
    echo "- Demo Portal: http://localhost:3000"
    echo "- API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🔐 Authentication:"
    echo "- Demo User: demo@biwoco.com / demo123"
    echo "- Admin User: admin@biwoco.com / admin123" 
    echo "- Or use 'Continue as Guest'"
    echo ""
    echo "📖 Documentation:"
    echo "- Setup Guide: README.md"
    echo "- Auth Setup: NEXTAUTH_SETUP.md"
    echo ""
    print_success "Ready to revolutionize customer support! 🚀"
}

# Run main function
main