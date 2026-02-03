#!/bin/bash

echo "=========================================="
echo "🚀 AI Voice Detection API - Railway Deploy"
echo "=========================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo ""
echo "🔐 Logging into Railway..."
railway login

# Initialize project
echo ""
echo "📦 Initializing Railway project..."
railway init

# Set environment variables
echo ""
echo "🔧 Setting environment variables..."
railway variables set API_KEYS="test-key-123,guvi-api-key-2024,demo-key-456"

# Deploy
echo ""
echo "🚀 Deploying to Railway..."
railway up

# Generate domain
echo ""
echo "🌐 Generating public domain..."
railway domain

# Show logs
echo ""
echo "📊 Showing deployment logs..."
railway logs

echo ""
echo "=========================================="
echo "✅ Deployment complete!"
echo "=========================================="
echo ""
echo "Your API is now live!"
echo "Run 'railway status' to check status"
echo "Run 'railway open' to view in browser"
echo ""
