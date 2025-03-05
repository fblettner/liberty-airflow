import os
from dotenv import load_dotenv

def load_env():
    """Load environment variables from a .env file."""
    if os.path.exists(".env"):
        load_dotenv(".env")
        print("Loaded environment variables from .env file.")
    else:
        print("No .env file found. Skipping environment variable loading.")