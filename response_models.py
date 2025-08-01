from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class MarketAnalysis(BaseModel):
    trend: str  # bullish, bearish, sideways, unknown
    volatility: str  # high, moderate, low, unknown
    confidence: float  # 0-100

class VolatilityIndicators(BaseModel):
    bollinger_bands_width: float
    average_true_range: float
    volatility_level: str

class OrderBlock(BaseModel):
    level: float
    type: str  # demand, supply
    strength: float  # 0-100
    timestamp: str

class FairValueGap(BaseModel):
    upper_level: float
    lower_level: float
    type: str  # bullish, bearish
    timestamp: str

class BreakOfStructure(BaseModel):
    level: float
    direction: str  # bullish, bearish
    strength: float
    timestamp: str

class ChangeOfCharacter(BaseModel):
    type: str  # bullish, bearish
    level: float
    strength: float
    timestamp: str

class LiquidityZone(BaseModel):
    upper_level: float
    lower_level: float
    volume: float
    type: str  # demand, supply
    timestamp: str

class AnchoredVWAP(BaseModel):
    anchor_point: float
    current_vwap: float
    anchor_type: str  # high, low
    timestamp: str

class RSIDivergence(BaseModel):
    type: str  # bullish, bearish
    rsi_value: float
    strength: float
    timestamp: str

class Recommendation(BaseModel):
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    reasoning: str

class ComparativeAnalysis(BaseModel):
    comparison_symbol: str
    correlation: float  # -1 to 1
    relative_strength: str  # outperforming, underperforming, neutral
    trend_alignment: bool

class CryptoAnalysisResponse(BaseModel):
    symbol: str
    timestamp: str
    timeframe: str
    market_analysis: MarketAnalysis
    volatility_indicators: VolatilityIndicators
    order_blocks: List[OrderBlock]
    fair_value_gaps: List[FairValueGap]
    break_of_structure: List[BreakOfStructure]
    change_of_character: List[ChangeOfCharacter]
    liquidity_zones: List[LiquidityZone]
    anchored_vwap: List[AnchoredVWAP]
    rsi_divergence: List[RSIDivergence]
    recommendation: Recommendation
    comparative_analysis: Optional[ComparativeAnalysis] = None
    metadata: Dict[str, Any]