ư#!/bin/bash

# Docker deployment script for BIWOCO AI Customer Support Assistant
# This script handles both development and production deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions for colored output
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

# Default values
ENVIRONMENT="development"
COMMAND="up"
BUILD=false
DETACH=false
SCALE_BACKEND=1
SCALE_FRONTEND=1

# Help function
show_help() {
    cat << EOF
BIWOCO AI Assistant Docker Deployment Script

Usage: $0 [OPTIONS]

OPTIONS:
    -e, --env ENVIRONMENT    Set environment (development|production) [default: development]
    -c, --command COMMAND    Docker compose command (up|down|restart|logs|status) [default: up]
    -b, --build             Force rebuild images
    -d, --detach            Run in detached mode
    -h, --help              Show this help message
    
    Production scaling options:
    --scale-backend N       Scale backend to N instances [default: 1]
    --scale-frontend N      Scale frontend to N instances [default: 1]

EXAMPLES:
    # Start development environment
    $0 -e development

    # Start production with rebuild
    $0 -e production -b -d

    # Scale production services
    $0 -e production --scale-backend 3 --scale-frontend 2

    # View logs
    $0 -c logs

    # Stop all services
    $0 -c down

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -c|--command)
            COMMAND="$2"
            shift 2
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        -d|--detach)
            DETACH=true
            shift
            ;;
        --scale-backend)
            SCALE_BACKEND="$2"
            shift 2
            ;;
        --scale-frontend)
            SCALE_FRONTEND="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Must be either 'development' or 'production'"
    exit 1
fi

print_status "Starting BIWOCO AI Assistant deployment..."
print_status "Environment: $ENVIRONMENT"
print_status "Command: $COMMAND"

# Set compose file based on environment
if [[ "$ENVIRONMENT" == "production" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_FILE=".env"
    
    # Check if production environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        print_error "Production environment file '$ENV_FILE' not found!"
        print_warning "Copy .env.docker to .env and configure your production settings"
        exit 1
    fi
else
    COMPOSE_FILE="docker-compose.yml"
    ENV_FILE=".env.local"
    
    # Create development .env.local if it doesn't exist
    if [[ ! -f "$ENV_FILE" ]]; then
        print_warning "Creating development environment file..."
        cp .env.local.example .env.local
    fi
fi

print_status "Using compose file: $COMPOSE_FILE"
print_status "Using environment file: $ENV_FILE"

# Pre-deployment checks
check_requirements() {
    print_status "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running!"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Build Docker options
build_docker_options() {
    local options=""
    
    # Add compose file
    options="$options -f $COMPOSE_FILE"
    
    # Add environment file
    options="$options --env-file $ENV_FILE"
    
    # Add build option
    if [[ "$BUILD" == true ]]; then
        options="$options --build"
    fi
    
    # Add detach option
    if [[ "$DETACH" == true ]]; then
        options="$options -d"
    fi
    
    echo "$options"
}

# Execute Docker Compose commands
execute_command() {
    local options=$(build_docker_options)
    
    case $COMMAND in
        up)
            print_status "Starting services..."
            if [[ "$ENVIRONMENT" == "production" ]]; then
                docker-compose $options up --scale backend=$SCALE_BACKEND --scale frontend=$SCALE_FRONTEND
            else
                docker-compose $options up
            fi
            ;;
        down)
            print_status "Stopping services..."
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
            ;;
        restart)
            print_status "Restarting services..."
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE restart
            ;;
        logs)
            print_status "Showing logs..."
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f --tail=100
            ;;
        status)
            print_status "Service status..."
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            exit 1
            ;;
    esac
}

# Post-deployment health checks
health_checks() {
    if [[ "$COMMAND" != "up" ]]; then
        return
    fi
    
    print_status "Performing health checks..."
    
    # Wait for services to start
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Backend is healthy"
    else
        print_warning "Backend health check failed"
    fi
    
    # Check frontend health (if accessible)
    if curl -f http://localhost:3000 &> /dev/null; then
        print_success "Frontend is healthy"
    else
        print_warning "Frontend health check failed"
    fi
    
    # Check database connection (if accessible)
    if docker exec -it biwoco-postgres-${ENVIRONMENT} pg_isready &> /dev/null; then
        print_success "Database is healthy"
    else
        print_warning "Database health check failed"
    fi
}

# Show service information
show_service_info() {
    if [[ "$COMMAND" != "up" ]] || [[ "$DETACH" != true ]]; then
        return
    fi
    
    echo ""
    print_success "BIWOCO AI Assistant is now running!"
    echo "=================================="
    echo ""
    echo "🌐 Application URLs:"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        echo "   Frontend: https://$DOMAIN"
        echo "   API Docs: https://$DOMAIN/docs"
        echo "   WebSocket: wss://$DOMAIN/ws"
    else
        echo "   Frontend: http://localhost:3000"
        echo "   API Docs: http://localhost:8000/docs"
        echo "   WebSocket: ws://localhost:8000/ws"
        echo "   Nginx: http://localhost"
    fi
    echo ""
    echo "🔐 Demo Accounts:"
    echo "   Demo User: demo@biwoco.com / demo123"
    echo "   Admin User: admin@biwoco.com / admin123"
    echo "   Or use 'Continue as Guest'"
    echo ""
    echo "🛠️  Management Commands:"
    echo "   View logs: $0 -c logs"
    echo "   Stop services: $0 -c down"
    echo "   Service status: $0 -c status"
    echo ""
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        echo "📊 Monitoring (if enabled):"
        echo "   Grafana: http://localhost:3001"
        echo "   Prometheus: http://localhost:9090"
        echo ""
    fi
    
    print_success "Deployment completed successfully! 🚀"
}

# Main execution
main() {
    check_requirements
    execute_command
    
    if [[ $? -eq 0 ]]; then
        health_checks
        show_service_info
    else
        print_error "Deployment failed!"
        exit 1
    fi
}

# Handle interruption
trap 'print_warning "Deployment interrupted by user"; exit 1' INT

# Run main function
main