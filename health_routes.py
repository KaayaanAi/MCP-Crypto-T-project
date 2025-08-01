from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "mcp-crypto-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/Docker deployments
    """
    # Check if required environment variables are set
    required_vars = ["BINANCE_API_KEY", "COINGECKO_API_KEY", "COINMARKETCAP_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        return {
            "status": "not_ready",
            "missing_env_vars": missing_vars,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "apis_configured": True
    }