# Model Setup and Caching

This document explains how to set up model caching to avoid downloading models every time you run the homeopathic AI agent.

## Quick Setup

1. **Install sentence-transformers** (if not already installed):
   ```bash
   pip install sentence-transformers
   ```

2. **Pre-download the model** (optional but recommended):
   ```bash
   python download_models.py
   ```

3. **Run the main script**:
   ```bash
   python ai_agent.py
   ```

## How Caching Works

The script automatically sets up local caching in the following directories:
- `./models/sentence_transformers/` - For sentence transformer models
- `./models/transformers/` - For transformer models cache

## Environment Variables

The script sets these environment variables automatically:
- `TRANSFORMERS_CACHE=./models/transformers`
- `SENTENCE_TRANSFORMERS_HOME=./models/sentence_transformers`

## Manual Model Download

If you want to manually download the model to avoid the first-run delay:

```python
from sentence_transformers import SentenceTransformer
import os

# Set cache directory
os.environ['SENTENCE_TRANSFORMERS_HOME'] = './models/sentence_transformers'

# Download and cache the model
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model downloaded and cached successfully!")
```

## Benefits

- **Faster startup**: No model download on subsequent runs
- **Offline capability**: Models work without internet after first download
- **Consistent performance**: Same model version across runs
- **Reduced bandwidth**: No repeated downloads

## Troubleshooting

If you encounter issues:

1. **Clear cache and re-download**:
   ```bash
   rm -rf models/
   python download_models.py
   ```

2. **Check disk space**: Models require ~100MB of space

3. **Network issues**: Ensure internet connection for first download

## Model Information

- **Model**: all-MiniLM-L6-v2
- **Size**: ~90MB
- **Dimensions**: 384
- **Use case**: Fast, lightweight sentence embeddings
- **Performance**: Good balance of speed and quality
