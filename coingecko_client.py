import aiohttp
import os
from typing import Dict, Any

class CoinGeckoClient:
    def __init__(self):
        self.api_key = os.getenv("COINGECKO_API_KEY")
        self.base_url = "https://api.coingecko.com/api/v3"
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make request to CoinGecko API"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key
            
        if params is None:
            params = {}
            
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"CoinGecko API error {response.status}: {error_text}")
    
    async def get_coin_data(self, symbol: str) -> Dict:
        """Get coin market data"""
        try:
            # Convert symbol to coin ID (simplified mapping)
            coin_id = self._symbol_to_coin_id(symbol)
            if not coin_id:
                return {}
                
            data = await self._make_request(f"/coins/{coin_id}")
            
            market_data = data.get("market_data", {})
            return {
                "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                "total_volume": market_data.get("total_volume", {}).get("usd", 0),
                "price_change_24h": market_data.get("price_change_percentage_24h", 0)
            }
        except Exception as e:
            print(f"Error fetching CoinGecko data: {e}")
            return {}
    
    def _symbol_to_coin_id(self, symbol: str) -> str:
        """Convert trading symbol to CoinGecko coin ID"""
        # Simple mapping for common pairs
        symbol_map = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum",
            "BNBUSDT": "binancecoin",
            "ADAUSDT": "cardano",
            "DOTUSDT": "polkadot",
            "LINKUSDT": "chainlink",
            "LTCUSDT": "litecoin",
            "BCHUSDT": "bitcoin-cash",
            "XLMUSDT": "stellar",
            "XRPUSDT": "ripple"
        }
        return symbol_map.get(symbol, "")