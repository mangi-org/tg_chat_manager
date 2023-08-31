import os
from dotenv import load_dotenv

load_dotenv(".env")
API_TOKEN = os.getenv("API_TOKEN")
TARGET_USER_ID = os.getenv("TARGET_USER_ID")