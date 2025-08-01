# MCP-Crypto API

Advanced cryptocurrency market analysis API service with comprehensive technical indicators and MCP/n8n compatibility.

## Features

- **Advanced Technical Analysis**
  - Order Blocks detection
  - Fair Value Gaps (FVG)
  - Break of Structure (BoS)
  - Change of Character (ChoCH)
  - Liquidity Zones
  - Anchored VWAP
  - RSI Divergence detection

- **Multi-Source Data Integration**
  - Binance API for real-time OHLCV data
  - CoinGecko API for market cap data
  - CoinMarketCap API for additional metrics

- **Volatility Analysis**
  - Bollinger Bands Width
  - Average True Range (ATR)
  - Dynamic volatility classification

- **Smart Recommendations**
  - BUY/SELL/HOLD signals
  - Confidence scoring
  - Comparative analysis with secondary symbols

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd mcp-crypto
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### 3. Local Development
```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

## API Configuration

### Required API Keys

1. **Binance API**
   - Create account at [binance.com](https://binance.com)
   - Generate API key in Account > API Management
   - Enable "Read Info" permissions

2. **CoinGecko API**
   - Get free API key at [coingecko.com](https://coingecko.com/api)
   - Pro plan recommended for production

3. **CoinMarketCap API**
   - Register at [coinmarketcap.com/api](https://coinmarketcap.com/api)
   - Free tier provides 10,000 calls/month

### Environment Variables
```bash
BINANCE_API_KEY=your_key_here
BINANCE_SECRET_KEY=your_secret_here
COINGECKO_API_KEY=your_key_here
COINMARKETCAP_API_KEY=your_key_here
PORT=8000
ENVIRONMENT=production
```

## API Endpoints

### Primary Analysis Endpoint
```http
GET /mcp/crypto?symbol=BTCUSDT&timeframe=1h&limit=500
```

**Parameters:**
- `symbol` (required): Trading pair (e.g., BTCUSDT, ETHUSDT)
- `timeframe` (optional): 1m, 5m, 15m, 1h, 4h, 1d (default: 1h)
- `limit` (optional): Number of candles (max 1000, default: 500)
- `comparison_symbol` (optional): Secondary symbol for comparative analysis

### Additional Endpoints
- `GET /health` - Health check
- `GET /health/ready` - Readiness check
- `GET /mcp/crypto/symbols` - Available trading symbols

## Example Response

```json
{
  "symbol": "BTCUSDT",
  "timestamp": "2024-12-19T10:30:00Z",
  "timeframe": "1h",
  "market_analysis": {
    "trend": "bullish",
    "volatility": "moderate",
    "confidence": 75.0
  },
  "volatility_indicators": {
    "bollinger_bands_width": 2.45,
    "average_true_range": 850.23,
    "volatility_level": "moderate"
  },
  "order_blocks": [
    {
      "level": 43250.50,
      "type": "demand",
      "strength": 85.2,
      "timestamp": "2024-12-19T09:00:00Z"
    }
  ],
  "fair_value_gaps": [
    {
      "upper_level": 43500.00,
      "lower_level": 43200.00,
      "type": "bullish",
      "timestamp": "2024-12-19T08:30:00Z"
    }
  ],
  "recommendation": {
    "action": "BUY",
    "confidence": 78.5,
    "reasoning": "Based on trend analysis (bullish), volatility (moderate), and technical indicators. Score: 1.23"
  }
}
```

## Production Deployment

### PM2 Process Management
```bash
# Install PM2 globally
npm install -g pm2

# Start application
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name mcp-crypto

# Save PM2 configuration
pm2 save
pm2 startup

# Monitor
pm2 logs mcp-crypto
pm2 monit
```

### Docker Production Setup
```bash
# Production build
docker build -t mcp-crypto:latest .

# Run with restart policy
docker run -d \
  --name mcp-crypto \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  mcp-crypto:latest
```

## n8n Integration

### MCP Client Node Configuration

1. Add HTTP Request node in n8n
2. Set URL: `http://your-server:8000/mcp/crypto`
3. Method: GET
4. Query Parameters:
   - symbol: {{ $json.symbol }}
   - timeframe: {{ $json.timeframe }}
   - limit: {{ $json.limit }}

### Example n8n Workflow
```json
{
  "nodes": [
    {
      "name": "MCP Crypto Analysis",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:8000/mcp/crypto",
        "qs": {
          "symbol": "BTCUSDT",
          "timeframe": "1h",
          "limit": 500
        }
      }
    }
  ]
}
```

## Development

### Project Structure
```
mcp-crypto/
├── main.py                 # FastAPI application
├── routes/
│   ├── crypto.py          # Crypto analysis routes
│   └── health.py          # Health check routes
├── services/
│   ├── crypto_analyzer.py # Main analysis engine
│   ├── binance_client.py  # Binance API client
│   ├── coingecko_client.py# CoinGecko API client
│   ├── coinmarketcap_client.py # CoinMarketCap client
│   └── technical_indicators.py # Technical analysis
├── models/
│   └── response.py        # Pydantic models
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Container build
└── .env.example          # Environment template
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

### Adding New Indicators

1. Add indicator function to `services/technical_indicators.py`
2. Update response model in `models/response.py`
3. Integrate in `services/crypto_analyzer.py`
4. Test with sample data

## Troubleshooting

### Common Issues

**API Key Errors**
- Verify all API keys are correctly set in `.env`
- Check API key permissions (Binance requires "Read Info")
- Ensure no trailing spaces in environment variables

**Rate Limiting**
- Binance: 1200 requests/minute
- CoinGecko: 50 calls/minute (free), 500/minute (pro)
- CoinMarketCap: 333 calls/day (free)

**Memory Issues**
- Reduce `limit` parameter for large datasets
- Monitor container memory usage
- Consider pagination for historical data

### Logs and Monitoring
```bash
# Docker logs
docker-compose logs -f mcp-crypto

# PM2 logs
pm2 logs mcp-crypto

# Health check
curl http://localhost:8000/health
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Open GitHub issue with detailed description

---

**Verified and ready for deployment** ✅
