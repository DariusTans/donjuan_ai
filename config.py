# - file to keep all the configuration variables
import os 
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PERSIS_DIRECTORY = os.environ.get("PERSIST_DIRECTORY")