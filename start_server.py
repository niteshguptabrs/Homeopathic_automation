#!/usr/bin/env python3
"""
Startup script for the Homeopathic AI server with proper agent initialization.
"""

import uvicorn
import asyncio
from ai_agent import get_homeopathic_agent

async def initialize_agent():
    """Pre-initialize the AI agent before starting the server"""
    print("🚀 Pre-initializing Homeopathic AI Agent...")
    try:
        agent = await get_homeopathic_agent()
        print("✅ AI Agent pre-initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to pre-initialize AI Agent: {e}")
        return False

def main():
    """Main function to start the server"""
    print("=== Homeopathic AI Server Startup ===\n")
    
    # Pre-initialize the agent
    print("Step 1: Initializing AI Agent...")
    success = asyncio.run(initialize_agent())
    
    if not success:
        print("⚠️ Warning: AI Agent initialization failed. Server will start but AI features may not work.")
        print("You can still use the form, but AI analysis will attempt initialization on first use.\n")
    
    print("Step 2: Starting FastAPI server...")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📋 Patient intake form: http://localhost:8000")
    print("🔍 Agent status: http://localhost:8000/agent-status")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=False,  # Disable reload to maintain agent state
        log_level="info"
    )

if __name__ == "__main__":
    main()
