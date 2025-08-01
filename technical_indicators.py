import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from models.response import *

class TechnicalIndicators:
    
    def determine_trend(self, df: pd.DataFrame) -> str:
        """Determine overall trend using multiple EMAs"""
        if len(df) < 50:
            return "unknown"
            
        # Calculate EMAs
        ema_9 = df['close'].ewm(span=9).mean()
        ema_21 = df['close'].ewm(span=21).mean()
        ema_50 = df['close'].ewm(span=50).mean()
        
        current_price = df['close'].iloc[-1]
        current_ema_9 = ema_9.iloc[-1]
        current_ema_21 = ema_21.iloc[-1]
        current_ema_50 = ema_50.iloc[-1]
        
        # Trend determination
        if (current_price > current_ema_9 > current_ema_21 > current_ema_50):
            return "bullish"
        elif (current_price < current_ema_9 < current_ema_21 < current_ema_50):
            return "bearish"
        else:
            return "sideways"
    
    def calculate_volatility_level(self, df: pd.DataFrame) -> str:
        """Calculate volatility level using ATR"""
        atr = self.average_true_range(df)
        if len(atr) == 0:
            return "unknown"
            
        current_atr = atr[-1]
        current_price = df['close'].iloc[-1]
        atr_percentage = (current_atr / current_price) * 100
        
        if atr_percentage > 5:
            return "high"
        elif atr_percentage > 2:
            return "moderate"
        else:
            return "low"
    
    def calculate_confidence(self, df: pd.DataFrame) -> float:
        """Calculate confidence level based on various factors"""
        confidence_factors = []
        
        # Volume trend
        if len(df) >= 20:
            volume_sma = df['volume'].rolling(20).mean()
            current_volume = df['volume'].iloc[-1]
            if current_volume > volume_sma.iloc[-1]:
                confidence_factors.append(20)
        
        # Price momentum
        if len(df) >= 14:
            rsi = self._calculate_rsi(df['close'], 14)
            if 30 <= rsi.iloc[-1] <= 70:  # Not overbought/oversold
                confidence_factors.append(25)
        
        # Trend consistency
        trend = self.determine_trend(df)
        if trend in ["bullish", "bearish"]:
            confidence_factors.append(30)
        
        return sum(confidence_factors) if confidence_factors else 50.0
    
    def bollinger_bands_width(self, df: pd.DataFrame, period: int = 20) -> np.ndarray:
        """Calculate Bollinger Bands Width"""
        sma = df['close'].rolling(period).mean()
        std = df['close'].rolling(period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        bb_width = ((upper - lower) / sma) * 100
        return bb_width.values
    
    def average_true_range(self, df: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate Average True Range"""
        if len(df) < period:
            return np.array([])
            
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = tr.rolling(period).mean()
        
        return atr.values
    
    def detect_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """Detect order blocks (institutional supply/demand zones)"""
        order_blocks = []
        
        if len(df) < 50:
            return order_blocks
        
        # Look for significant volume spikes with price moves
        volume_mean = df['volume'].rolling(20).mean()
        volume_std = df['volume'].rolling(20).std()
        
        for i in range(20, len(df) - 5):
            volume_threshold = volume_mean.iloc[i] + (2 * volume_std.iloc[i])
            
            if df['volume'].iloc[i] > volume_threshold:
                # Check for significant price move
                price_change = abs(df['close'].iloc[i] - df['open'].iloc[i])
                avg_range = df['high'].iloc[i-10:i].mean() - df['low'].iloc[i-10:i].mean()
                
                if price_change > avg_range * 0.5:
                    block_type = "demand" if df['close'].iloc[i] > df['open'].iloc[i] else "supply"
                    
                    order_blocks.append(OrderBlock(
                        level=float(df['close'].iloc[i]),
                        type=block_type,
                        strength=min(price_change / avg_range * 50, 100),
                        timestamp=df.index[i].isoformat()
                    ))
        
        return order_blocks[-10:]  # Return last 10 order blocks
    
    def detect_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """Detect Fair Value Gaps (price gaps)"""
        fvgs = []
        
        for i in range(2, len(df)):
            # Bullish FVG: current low > previous high
            if df['low'].iloc[i] > df['high'].iloc[i-2]:
                fvgs.append(FairValueGap(
                    upper_level=float(df['low'].iloc[i]),
                    lower_level=float(df['high'].iloc[i-2]),
                    type="bullish",
                    timestamp=df.index[i].isoformat()
                ))
            
            # Bearish FVG: current high < previous low
            elif df['high'].iloc[i] < df['low'].iloc[i-2]:
                fvgs.append(FairValueGap(
                    upper_level=float(df['low'].iloc[i-2]),
                    lower_level=float(df['high'].iloc[i]),
                    type="bearish",
                    timestamp=df.index[i].isoformat()
                ))
        
        return fvgs[-5:]  # Return last 5 FVGs
    
    def detect_break_of_structure(self, df: pd.DataFrame) -> List[BreakOfStructure]:
        """Detect Break of Structure (BOS)"""
        bos_list = []
        
        if len(df) < 20:
            return bos_list
        
        # Find recent highs and lows
        highs = df['high'].rolling(5, center=True).max()
        lows = df['low'].rolling(5, center=True).min()
        
        for i in range(10, len(df) - 5):
            # Bullish BOS: Price breaks above recent high
            recent_high = highs.iloc[i-10:i].max()
            if df['close'].iloc[i] > recent_high and recent_high > 0:
                bos_list.append(BreakOfStructure(
                    level=float(recent_high),
                    direction="bullish",
                    strength=((df['close'].iloc[i] - recent_high) / recent_high) * 100,
                    timestamp=df.index[i].isoformat()
                ))
            
            # Bearish BOS: Price breaks below recent low
            recent_low = lows.iloc[i-10:i].min()
            if df['close'].iloc[i] < recent_low and recent_low > 0:
                bos_list.append(BreakOfStructure(
                    level=float(recent_low),
                    direction="bearish",
                    strength=((recent_low - df['close'].iloc[i]) / recent_low) * 100,
                    timestamp=df.index[i].isoformat()
                ))
        
        return bos_list[-3:]  # Return last 3 BOS
    
    def detect_change_of_character(self, df: pd.DataFrame) -> List[ChangeOfCharacter]:
        """Detect Change of Character (ChoCH)"""
        choch_list = []
        
        if len(df) < 30:
            return choch_list
        
        # Calculate short and long EMAs
        ema_short = df['close'].ewm(span=9).mean()
        ema_long = df['close'].ewm(span=21).mean()
        
        for i in range(21, len(df)):
            # Bullish ChoCH: EMA crossover from bearish to bullish
            if (ema_short.iloc[i] > ema_long.iloc[i] and 
                ema_short.iloc[i-1] <= ema_long.iloc[i-1]):
                
                choch_list.append(ChangeOfCharacter(
                    type="bullish",
                    level=float(df['close'].iloc[i]),
                    strength=abs(ema_short.iloc[i] - ema_long.iloc[i]) / ema_long.iloc[i] * 100,
                    timestamp=df.index[i].isoformat()
                ))
            
            # Bearish ChoCH: EMA crossover from bullish to bearish
            elif (ema_short.iloc[i] < ema_long.iloc[i] and 
                  ema_short.iloc[i-1] >= ema_long.iloc[i-1]):
                
                choch_list.append(ChangeOfCharacter(
                    type="bearish",
                    level=float(df['close'].iloc[i]),
                    strength=abs(ema_short.iloc[i] - ema_long.iloc[i]) / ema_long.iloc[i] * 100,
                    timestamp=df.index[i].isoformat()
                ))
        
        return choch_list[-3:]  # Return last 3 ChoCH
    
    def detect_liquidity_zones(self, df: pd.DataFrame) -> List[LiquidityZone]:
        """Detect liquidity zones (areas of high volume)"""
        liquidity_zones = []
        
        if len(df) < 20:
            return liquidity_zones
        
        # Find volume clusters
        volume_mean = df['volume'].rolling(10).mean()
        
        for i in range(10, len(df)):
            if df['volume'].iloc[i] > volume_mean.iloc[i] * 1.5:
                zone_type = "demand" if df['close'].iloc[i] > df['open'].iloc[i] else "supply"
                
                liquidity_zones.append(LiquidityZone(
                    upper_level=float(df['high'].iloc[i]),
                    lower_level=float(df['low'].iloc[i]),
                    volume=float(df['volume'].iloc[i]),
                    type=zone_type,
                    timestamp=df.index[i].isoformat()
                ))
        
        return liquidity_zones[-5:]  # Return last 5 zones
    
    def calculate_anchored_vwap(self, df: pd.DataFrame) -> List[AnchoredVWAP]:
        """Calculate Anchored VWAP from significant price points"""
        anchored_vwaps = []
        
        if len(df) < 50:
            return anchored_vwaps
        
        # Find significant high/low points for anchoring
        highs = df['high'].rolling(10, center=True).max()
        lows = df['low'].rolling(10, center=True).min()
        
        significant_points = []
        for i in range(10, len(df) - 10):
            if df['high'].iloc[i] == highs.iloc[i]:
                significant_points.append((i, 'high'))
            elif df['low'].iloc[i] == lows.iloc[i]:
                significant_points.append((i, 'low'))
        
        # Calculate VWAP from last few significant points
        for anchor_idx, anchor_type in significant_points[-3:]:
            vwap_values = []
            cumulative_pv = 0
            cumulative_volume = 0
            
            for i in range(anchor_idx, len(df)):
                typical_price = (df['high'].iloc[i] + df['low'].iloc[i] + df['close'].iloc[i]) / 3
                volume = df['volume'].iloc[i]
                
                cumulative_pv += typical_price * volume
                cumulative_volume += volume
                
                if cumulative_volume > 0:
                    vwap = cumulative_pv / cumulative_volume
                    vwap_values.append(vwap)
            
            if vwap_values:
                anchored_vwaps.append(AnchoredVWAP(
                    anchor_point=float(df['high'].iloc[anchor_idx] if anchor_type == 'high' else df['low'].iloc[anchor_idx]),
                    current_vwap=float(vwap_values[-1]),
                    anchor_type=anchor_type,
                    timestamp=df.index[anchor_idx].isoformat()
                ))
        
        return anchored_vwaps
    
    def detect_rsi_divergence(self, df: pd.DataFrame, period: int = 14) -> List[RSIDivergence]:
        """Detect RSI divergences"""
        divergences = []
        
        if len(df) < period * 3:
            return divergences
        
        rsi = self._calculate_rsi(df['close'], period)
        
        # Find price and RSI highs/lows
        price_highs = df['high'].rolling(5, center=True).max()
        price_lows = df['low'].rolling(5, center=True).min()
        rsi_highs = rsi.rolling(5, center=True).max()
        rsi_lows = rsi.rolling(5, center=True).min()
        
        for i in range(period + 10, len(df) - 5):
            # Bullish divergence: price makes lower low, RSI makes higher low
            if (df['low'].iloc[i] == price_lows.iloc[i] and 
                rsi.iloc[i] == rsi_lows.iloc[i]):
                
                # Look for previous low
                for j in range(max(0, i-20), i-5):
                    if (df['low'].iloc[j] == price_lows.iloc[j] and
                        rsi.iloc[j] == rsi_lows.iloc[j]):
                        
                        if (df['low'].iloc[i] < df['low'].iloc[j] and
                            rsi.iloc[i] > rsi.iloc[j]):
                            
                            divergences.append(RSIDivergence(
                                type="bullish",
                                rsi_value=float(rsi.iloc[i]),
                                strength=(rsi.iloc[i] - rsi.iloc[j]) * 2,
                                timestamp=df.index[i].isoformat()
                            ))
                        break
            
            # Bearish divergence: price makes higher high, RSI makes lower high
            if (df['high'].iloc[i] == price_highs.iloc[i] and 
                rsi.iloc[i] == rsi_highs.iloc[i]):
                
                # Look for previous high
                for j in range(max(0, i-20), i-5):
                    if (df['high'].iloc[j] == price_highs.iloc[j] and
                        rsi.iloc[j] == rsi_highs.iloc[j]):
                        
                        if (df['high'].iloc[i] > df['high'].iloc[j] and
                            rsi.iloc[i] < rsi.iloc[j]):
                            
                            divergences.append(RSIDivergence(
                                type="bearish",
                                rsi_value=float(rsi.iloc[i]),
                                strength=(rsi.iloc[j] - rsi.iloc[i]) * 2,
                                timestamp=df.index[i].isoformat()
                            ))
                        break
        
        return divergences[-2:]  # Return last 2 divergences
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi