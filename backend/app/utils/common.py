import os
from dotenv import load_dotenv

def load_env():
    """Load environment variables from a .env file."""
    if os.path.exists(".env"):
        load_dotenv(".env")
    else:
        print("No .env file found. Skipping environment variable loading.")

class PoolConfig:
    def __init__(self, user, password, host, port, database, pool_min, pool_max, pool_alias):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.pool_min = pool_min
        self.pool_max = pool_max
        self.pool_alias = pool_alias