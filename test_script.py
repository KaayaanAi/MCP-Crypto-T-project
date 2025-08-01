import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_api():
    """Test the MCP-Crypto API endpoints"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("Testing health endpoint...")
        async with session.get(f"{base_url}/mcp/crypto", params=params) as response:
            if response.status == 200:
                data = await response.json()
                print("✅ Crypto analysis endpoint working")
                print(f"   Symbol: {data['symbol']}")
                print(f"   Trend: {data['market_analysis']['trend']}")
                print(f"   Volatility: {data['market_analysis']['volatility']}")
                print(f"   Recommendation: {data['recommendation']['action']}")
                print(f"   Confidence: {data['recommendation']['confidence']:.1f}%")
            else:
                error_text = await response.text()
                print(f"❌ Crypto analysis failed: {response.status}")
                print(f"   Error: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_api())"{base_url}/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health check passed: {data['status']}")
            else:
                print(f"❌ Health check failed: {response.status}")
                return
        
        # Test readiness endpoint
        print("Testing readiness endpoint...")
        async with session.get(f"{base_url}/health/ready") as response:
            data = await response.json()
            if data.get("status") == "ready":
                print("✅ Readiness check passed")
            else:
                print(f"⚠️ Not ready: {data}")
        
        # Test crypto analysis endpoint
        print("Testing crypto analysis endpoint...")
        params = {
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "limit": 100
        }
        
        async with session.get(f