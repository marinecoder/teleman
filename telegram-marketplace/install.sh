#!/bin/bash
# Installation and startup script for Telegram Marketplace

echo "🚀 Installing Telegram Marketplace System..."

# Check if we're in the right directory
if [ ! -d "telegram-marketplace" ]; then
    echo "❌ Error: telegram-marketplace directory not found"
    echo "Please run this script from the root directory"
    exit 1
fi

cd telegram-marketplace

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd server
pip install -r ../requirements.txt
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd client
npm install
cd ..

# Create sessions directory
mkdir -p server/sessions

# Copy environment template
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "⚙️  Environment file created. Please edit .env with your API credentials."
fi

echo "✅ Installation complete!"
echo ""
echo "🏃 To start the application:"
echo "  Backend: cd server && python main.py"
echo "  Frontend: cd client && npm run dev"
echo ""
echo "📝 Don't forget to:"
echo "  1. Edit .env file with your Telegram API credentials"
echo "  2. Start Redis server: redis-server"
echo "  3. Configure your proxy list in .env"
