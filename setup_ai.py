#!/usr/bin/env python3
"""
Setup script for Homeopathic AI Agent
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "knowledge_base/pdfs",
        "vector_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_environment():
    """Check if environment variables are set"""
    required_vars = [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_SEARCH_ENGINE_ID"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("\n❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\n📝 Please create a .env file with these variables")
        print("   Copy .env.example to .env and fill in your API keys")
        return False
    
    print("✓ All environment variables are set")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    os.system("pip install -r requirements_ai.txt")
    print("✓ Dependencies installed")

def setup_knowledge_base():
    """Setup instructions for knowledge base"""
    pdf_dir = Path("knowledge_base/pdfs")
    
    print(f"\n📚 Knowledge Base Setup:")
    print(f"   Add your homeopathic PDF references to: {pdf_dir}")
    print("\n   Recommended PDFs:")
    print("   - Boericke's Materia Medica")
    print("   - Kent's Repertory") 
    print("   - Organon of Medicine")
    print("   - Clarke's Dictionary")
    print("   - Allen's Keynotes")
    print("   - Modern research papers")

def main():
    """Main setup function"""
    print("🏥 Setting up Homeopathic AI Agent...")
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Check environment
    env_ok = check_environment()
    
    # Setup knowledge base
    setup_knowledge_base()
    
    print("\n🎉 Setup complete!")
    
    if not env_ok:
        print("\n⚠️  Don't forget to set up your .env file before running the agent")
    
    print("\n🚀 To test the agent, run: python ai_agent.py")

if __name__ == "__main__":
    main()