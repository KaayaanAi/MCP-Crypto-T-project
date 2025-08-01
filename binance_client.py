import aiohttp
import hashlib
import hmac
import time
import os
from typing import List, Dict, Any
from urllib.parse import urlencode

class BinanceClient:
    def __init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_SECRET_KEY")
        self.base_url = "https://api.binance.com/api/v3"
        
    def _create_signature(self, query_string: str) -> str:
        """Create HMAC SHA256 signature for Binance API"""
        if not self.api_secret:
            return ""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None, signed: bool = False) -> Dict:
        """Make authenticated request to Binance API"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key
        
        if params is None:
            params = {}
            
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            query_string = urlencode(params)
            params["signature"] = self._create_signature(query_string)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Binance API error {response.status}: {error_text}")
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List:
        """Get kline/candlestick data"""
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": min(limit, 1000)  # Binance max is 1000
        }
        return await self._make_request("/klines", params)
    
    async def get_24h_ticker(self, symbol: str) -> Dict:
        """Get 24hr ticker price change statistics"""
        params = {"symbol": symbol}
        return await self._make_request("/ticker/24hr", params)
    
    async def get_exchange_info(self) -> List[str]:
        """Get exchange trading rules and symbol information"""
        data = await self._make_request("/exchangeInfo")
        symbols = [s["symbol"] for s in data.get("symbols", []) if s.get("status") == "TRADING"]
        return symbols[:100]  # Return first 100 active symbols
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book for symbol"""
        params = {
            "symbol": symbol,
            "limit": limit
        }
        return await self._make_request("/depth", params)