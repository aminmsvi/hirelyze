import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Application configuration class.
    Loads environment variables and provides default values for prompts and other settings.
    """

    LLM_MODEL: str = os.getenv("LLM_MODEL")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL")

# Initialize a global config object
settings = Config()
