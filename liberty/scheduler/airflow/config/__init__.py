import os
from pathlib import Path

# Get the base directory of the package
BASE_DIR = Path(__file__).resolve().parent

def get_config_path():
    """Return the absolute path to logs-frontend-text.log"""
    return str(BASE_DIR)
