# backend/app/model_loader.py

from sentence_transformers import SentenceTransformer

print("Downloading and caching Hugging Face model 'all-MiniLM-L6-v2'...")

# This line will download the model from the Hub and save it to a cache directory
SentenceTransformer('all-MiniLM-L6-v2')

print("Model download complete.")