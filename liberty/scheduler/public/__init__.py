import os
from pathlib import Path

# Get the base directory of the package
BASE_DIR = Path(__file__).resolve().parent

OFFLINE_PATH = BASE_DIR / "offline/index.html"
FRONTEND_PATH = BASE_DIR / "frontend/index.html"
OFFLINE_ASSETS_PATH = BASE_DIR / "offline/assets"
FRONTEND_ASSETS_PATH = BASE_DIR / "frontend/assets"

def get_offline_path():
    return str(OFFLINE_PATH)

def get_frontend_path():
    return str(FRONTEND_PATH)

def get_offline_assets_path():
    return str(OFFLINE_ASSETS_PATH)

def get_frontend_assets_path():
    return str(FRONTEND_ASSETS_PATH)