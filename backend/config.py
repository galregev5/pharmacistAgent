import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Basic configuration object
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
