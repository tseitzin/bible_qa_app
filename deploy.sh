#!/bin/bash

# Bible Q&A App Deployment Script for Heroku
# This script handles deploying backend and frontend from a monorepo

set -e  # Exit on error

echo "🚀 Bible Q&A App - Heroku Deployment"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI is not installed. Please install it first:"
    echo "  brew tap heroku/brew && brew install heroku"
    exit 1
fi

print_success "Heroku CLI found"

# Login check
if ! heroku auth:whoami &> /dev/null; then
    print_info "Please login to Heroku..."
    heroku login
fi

print_success "Logged in to Heroku"

# Deployment menu
echo ""
echo "What would you like to deploy?"
echo "1) Backend only"
echo "2) Frontend only"
echo "3) Both (Backend first, then Frontend)"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        print_info "Deploying Backend..."
        cd backend
        
        # Check if Heroku app exists
        if ! heroku apps:info &> /dev/null; then
            print_info "No Heroku app found. Creating one..."
            read -p "Enter your backend app name (e.g., bible-qa-backend-yourname): " backend_app
            heroku create "$backend_app"
            
            # Add PostgreSQL
            print_info "Adding PostgreSQL database..."
            heroku addons:create heroku-postgresql:essential-0
            
            # Set environment variables
            read -p "Enter your OpenAI API key: " openai_key
            heroku config:set OPENAI_API_KEY="$openai_key"
            heroku config:set ALLOWED_ORIGINS=http://localhost:5173
            heroku config:set DEBUG=false
        fi
        
        # Deploy
        print_info "Pushing to Heroku..."
        git subtree push --prefix backend heroku main || git push heroku `git subtree split --prefix backend main`:main --force
        
        print_info "Running database migrations..."
        heroku run python -m alembic upgrade head
        
        print_success "Backend deployed successfully!"
        heroku open
        ;;
        
    2)
        echo ""
        print_info "Deploying Frontend..."
        cd frontend
        
        # Check if Heroku app exists
        if ! heroku apps:info &> /dev/null; then
            print_info "No Heroku app found. Creating one..."
            read -p "Enter your frontend app name (e.g., bible-qa-frontend-yourname): " frontend_app
            heroku create "$frontend_app"
            
            # Set environment variables
            read -p "Enter your backend URL (e.g., https://your-backend.herokuapp.com): " backend_url
            heroku config:set VITE_API_URL="$backend_url"
            heroku config:set NODE_ENV=production
        fi
        
        # Build locally
        print_info "Building frontend..."
        npm install
        npm run build
        
        # Deploy
        print_info "Pushing to Heroku..."
        git subtree push --prefix frontend heroku main || git push heroku `git subtree split --prefix frontend main`:main --force
        
        print_success "Frontend deployed successfully!"
        heroku open
        ;;
        
    3)
        echo ""
        print_info "Deploying Backend first..."
        # Run backend deployment
        $0 1
        
        echo ""
        print_info "Now deploying Frontend..."
        # Run frontend deployment
        $0 2
        
        print_success "Both apps deployed successfully!"
        ;;
        
    4)
        print_info "Exiting..."
        exit 0
        ;;
        
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
print_info "Deployment complete!"
print_info "Remember to update CORS settings:"
echo "  cd backend"
echo "  heroku config:set ALLOWED_ORIGINS=https://your-frontend-app.herokuapp.com,http://localhost:5173"
