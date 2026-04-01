import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).parent / "data" / "recipes.db"))
UPLOAD_PATH = os.getenv("UPLOAD_PATH", str(Path(__file__).parent / "data" / "images"))

# Ensure directories exist
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
