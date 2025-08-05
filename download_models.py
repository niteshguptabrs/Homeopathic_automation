#!/usr/bin/env python3
"""
Script to pre-download and cache models for the homeopathic AI agent.
Run this once to avoid downloading models every time the main script runs.
"""

import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    try:
        import sentence_transformers
        print("✓ sentence-transformers already installed")
        return True
    except ImportError:
        print("Installing sentence-transformers...")
        os.system("pip install sentence-transformers")
        return True

def download_sentence_transformer_model():
    """Download and cache the sentence transformer model"""
    try:
        print("Downloading sentence transformer model...")
        from sentence_transformers import SentenceTransformer
        
        # Create models directory
        models_dir = Path("models/sentence_transformers")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Download and cache the model
        print("Downloading all-MiniLM-L6-v2 model...")
        model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            cache_folder=str(models_dir)
        )
        
        # Test the model to ensure it works
        test_text = ["This is a test sentence"]
        embeddings = model.encode(test_text)
        print(f"✓ Model downloaded and tested successfully!")
        print(f"✓ Model cached in: {models_dir.absolute()}")
        print(f"✓ Embedding dimension: {embeddings.shape[1]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error downloading model: {e}")
        return False

def main():
    """Main function to download all required models"""
    print("=== Homeopathic AI Agent - Model Download Script ===\n")
    
    # Install requirements
    if not install_requirements():
        print("✗ Failed to install requirements")
        return False
    
    # Download sentence transformer model
    if not download_sentence_transformer_model():
        print("✗ Failed to download sentence transformer model")
        return False
    
    print("\n=== All models downloaded successfully! ===")
    print("You can now run the main ai_agent.py script without waiting for model downloads.")
    
    return True

if __name__ == "__main__":
    main()
