import os

from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")
AUTHOR = os.getenv("AUTHOR")
LANGUAGE = os.getenv("LANGUAGE")
