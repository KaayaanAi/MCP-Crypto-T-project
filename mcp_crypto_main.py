from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from routes.crypto import router as crypto_router
from routes.health import router as health_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MCP-Crypto API",
    description="Advanced cryptocurrency market analysis API service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(crypto_router, prefix="/mcp")
app.include_router(health_router)

@app.get("/")
async def root():
    return {
        "message": "MCP-Crypto API",
        "version": "1.0.0",
        "endpoints": {
            "crypto_analysis": "/mcp/crypto",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )