#!/bin/bash

# MCP-Crypto Quick Setup Script
echo "🚀 Setting up MCP-Crypto API..."

# Check Python version
echo "📋 Checking Python version..."
python3 --version || { echo "❌ Python 3.12+ required"; exit 1; }

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p routes services models

# Create __init__.py files
echo "📄 Creating package files..."
touch routes/__init__.py
touch services/__init__.py  
touch models/__init__.py

# Copy environment template
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Please edit .env with your API keys:"
    echo "   - BINANCE_API_KEY"
    echo "   - BINANCE_SECRET_KEY" 
    echo "   - COINGECKO_API_KEY"
    echo "   - COINMARKETCAP_API_KEY"
fi

echo "✅ Setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo "4. Test: curl http://localhost:8000/health"
echo ""
echo "🐳 Or use Docker:"
echo "docker-compose up -d"