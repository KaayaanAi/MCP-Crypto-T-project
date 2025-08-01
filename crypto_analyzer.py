import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import os
from dataclasses import asdict

from .binance_client import BinanceClient
from .coingecko_client import CoinGeckoClient
from .coinmarketcap_client import CoinMarketCapClient
from .technical_indicators import TechnicalIndicators
from models.response import *

class CryptoAnalyzer:
    def __init__(self):
        self.binance = BinanceClient()
        self.coingecko = CoinGeckoClient()
        self.cmc = CoinMarketCapClient()
        self.ti = TechnicalIndicators()
    
    async def analyze(
        self, 
        symbol: str, 
        comparison_symbol: Optional[str] = None,
        timeframe: str = "1h",
        limit: int = 500
    ) -> CryptoAnalysisResponse:
        """
        Perform comprehensive cryptocurrency analysis
        """
        # Get OHLCV data
        ohlcv_data = await self.binance.get_klines(symbol, timeframe, limit)
        df = self._create_dataframe(ohlcv_data)
        
        # Get additional market data
        market_data = await self._get_market_data(symbol)
        
        # Calculate all technical indicators
        analysis = await self._perform_technical_analysis(df, symbol)
        
        # Comparative analysis if requested
        comparative_analysis = None
        if comparison_symbol:
            comparative_analysis = await self._perform_comparative_analysis(
                symbol, comparison_symbol, timeframe, limit
            )
        
        # Generate final recommendation
        recommendation = self._generate_recommendation(analysis, df)
        
        return CryptoAnalysisResponse(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc).isoformat(),
            timeframe=timeframe,
            market_analysis=analysis["market_analysis"],
            volatility_indicators=analysis["volatility_indicators"],
            order_blocks=analysis["order_blocks"],
            fair_value_gaps=analysis["fair_value_gaps"],
            break_of_structure=analysis["break_of_structure"],
            change_of_character=analysis["change_of_character"],
            liquidity_zones=analysis["liquidity_zones"],
            anchored_vwap=analysis["anchored_vwap"],
            rsi_divergence=analysis["rsi_divergence"],
            recommendation=recommendation,
            comparative_analysis=comparative_analysis,
            metadata={
                "data_points": len(df),
                "price_change_24h": market_data.get("price_change_24h", 0),
                "volume_24h": market_data.get("volume_24h", 0),
                "market_cap": market_data.get("market_cap", 0)
            }
        )
    
    def _create_dataframe(self, ohlcv_data: List) -> pd.DataFrame:
        """Convert OHLCV data to pandas DataFrame"""
        df = pd.DataFrame(ohlcv_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Convert to appropriate types
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        return df
    
    async def _get_market_data(self, symbol: str) -> Dict:
        """Get additional market data from multiple sources"""
        try:
            # Get 24h ticker data from Binance
            ticker_data = await self.binance.get_24h_ticker(symbol)
            
            # Get market cap data from CoinGecko (if available)
            market_cap_data = await self.coingecko.get_coin_data(symbol)
            
            return {
                "price_change_24h": float(ticker_data.get("priceChangePercent", 0)),
                "volume_24h": float(ticker_data.get("volume", 0)),
                "market_cap": market_cap_data.get("market_cap", 0)
            }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {"price_change_24h": 0, "volume_24h": 0, "market_cap": 0}
    
    async def _perform_technical_analysis(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Perform comprehensive technical analysis"""
        
        # Market Analysis
        market_analysis = MarketAnalysis(
            trend=self.ti.determine_trend(df),
            volatility=self.ti.calculate_volatility_level(df),
            confidence=self.ti.calculate_confidence(df)
        )
        
        # Volatility Indicators
        bb_width = self.ti.bollinger_bands_width(df)
        atr = self.ti.average_true_range(df)
        
        volatility_indicators = VolatilityIndicators(
            bollinger_bands_width=bb_width[-1] if len(bb_width) > 0 else 0,
            average_true_range=atr[-1] if len(atr) > 0 else 0,
            volatility_level=market_analysis.volatility
        )
        
        # Advanced Technical Indicators
        order_blocks = self.ti.detect_order_blocks(df)
        fair_value_gaps = self.ti.detect_fair_value_gaps(df)
        break_of_structure = self.ti.detect_break_of_structure(df)
        change_of_character = self.ti.detect_change_of_character(df)
        liquidity_zones = self.ti.detect_liquidity_zones(df)
        anchored_vwap = self.ti.calculate_anchored_vwap(df)
        rsi_divergence = self.ti.detect_rsi_divergence(df)
        
        return {
            "market_analysis": market_analysis,
            "volatility_indicators": volatility_indicators,
            "order_blocks": order_blocks,
            "fair_value_gaps": fair_value_gaps,
            "break_of_structure": break_of_structure,
            "change_of_character": change_of_character,
            "liquidity_zones": liquidity_zones,
            "anchored_vwap": anchored_vwap,
            "rsi_divergence": rsi_divergence
        }
    
    async def _perform_comparative_analysis(
        self, 
        symbol: str, 
        comparison_symbol: str,
        timeframe: str,
        limit: int
    ) -> ComparativeAnalysis:
        """Perform comparative analysis between two symbols"""
        try:
            # Get data for comparison symbol
            comp_data = await self.binance.get_klines(comparison_symbol, timeframe, limit)
            comp_df = self._create_dataframe(comp_data)
            
            # Calculate correlation
            correlation = np.corrcoef(
                self._create_dataframe(await self.binance.get_klines(symbol, timeframe, limit))['close'].values,
                comp_df['close'].values
            )[0, 1]
            
            # Compare trends
            main_trend = self.ti.determine_trend(self._create_dataframe(await self.binance.get_klines(symbol, timeframe, limit)))
            comp_trend = self.ti.determine_trend(comp_df)
            
            return ComparativeAnalysis(
                comparison_symbol=comparison_symbol,
                correlation=float(correlation) if not np.isnan(correlation) else 0.0,
                relative_strength="outperforming" if main_trend == "bullish" and comp_trend != "bullish" else 
                                "underperforming" if main_trend != "bullish" and comp_trend == "bullish" else "neutral",
                trend_alignment=main_trend == comp_trend
            )
        except Exception as e:
            print(f"Error in comparative analysis: {e}")
            return ComparativeAnalysis(
                comparison_symbol=comparison_symbol,
                correlation=0.0,
                relative_strength="neutral",
                trend_alignment=False
            )
    
    def _generate_recommendation(self, analysis: Dict, df: pd.DataFrame) -> Recommendation:
        """Generate trading recommendation based on analysis"""
        
        # Score different factors
        trend_score = 1 if analysis["market_analysis"].trend == "bullish" else -1 if analysis["market_analysis"].trend == "bearish" else 0
        volatility_score = -0.5 if analysis["market_analysis"].volatility == "high" else 0.5 if analysis["market_analysis"].volatility == "low" else 0
        
        # RSI considerations
        rsi_score = 0
        if analysis["rsi_divergence"]:
            for divergence in analysis["rsi_divergence"]:
                if divergence.type == "bullish":
                    rsi_score += 0.5
                elif divergence.type == "bearish":
                    rsi_score -= 0.5
        
        # Structure breaks
        structure_score = 0
        if analysis["break_of_structure"]:
            for bos in analysis["break_of_structure"]:
                if bos.direction == "bullish":
                    structure_score += 0.3
                else:
                    structure_score -= 0.3
        
        # Calculate total score
        total_score = trend_score + volatility_score + rsi_score + structure_score
        
        # Generate recommendation
        if total_score > 0.5:
            action = "BUY"
        elif total_score < -0.5:
            action = "SELL"
        else:
            action = "HOLD"
        
        confidence = min(abs(total_score) * 100, 100)
        
        return Recommendation(
            action=action,
            confidence=confidence,
            reasoning=f"Based on trend analysis ({analysis['market_analysis'].trend}), "
                     f"volatility ({analysis['market_analysis'].volatility}), "
                     f"and technical indicators. Score: {total_score:.2f}"
        )
    
    async def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        return await self.binance.get_exchange_info()