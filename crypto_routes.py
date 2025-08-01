from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.crypto_analyzer import CryptoAnalyzer
from models.response import CryptoAnalysisResponse
import asyncio

router = APIRouter()

@router.get("/crypto", response_model=CryptoAnalysisResponse)
async def analyze_crypto(
    symbol: str = Query(..., description="Trading pair symbol (e.g., BTCUSDT)"),
    comparison_symbol: Optional[str] = Query(None, description="Optional comparison symbol for relative analysis"),
    timeframe: str = Query("1h", description="Timeframe for analysis (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(500, description="Number of candles to fetch (max 1000)")
):
    """
    Perform comprehensive cryptocurrency market analysis
    """
    try:
        analyzer = CryptoAnalyzer()
        
        # Validate inputs
        if limit > 1000:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 1000")
        
        valid_timeframes = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
        if timeframe not in valid_timeframes:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe. Must be one of: {valid_timeframes}")
        
        # Perform analysis
        result = await analyzer.analyze(
            symbol=symbol.upper(),
            comparison_symbol=comparison_symbol.upper() if comparison_symbol else None,
            timeframe=timeframe,
            limit=limit
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/crypto/symbols")
async def get_available_symbols():
    """
    Get list of available trading symbols
    """
    try:
        analyzer = CryptoAnalyzer()
        symbols = await analyzer.get_available_symbols()
        return {"symbols": symbols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch symbols: {str(e)}")