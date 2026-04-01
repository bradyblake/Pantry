from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_path: Path = Path(__file__).parent.parent / "data" / "pantrypal.db"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS - allow frontend dev server and production
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    # Set CORS_ORIGINS env var to comma-separated URLs for production, e.g.:
    # CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173

    # AI Provider for recipe parsing: "gemini", "groq", or "claude"
    # Can also be comma-separated for fallback order: "gemini,groq"
    ai_provider: str = "gemini"

    # API Keys - comma-separated for multiple keys that rotate on rate limit
    # Example: GEMINI_API_KEY=key1,key2,key3
    gemini_api_keys: Optional[str] = None     # GEMINI_API_KEYS (or GEMINI_API_KEY)
    groq_api_keys: Optional[str] = None       # GROQ_API_KEYS (or GROQ_API_KEY)
    anthropic_api_keys: Optional[str] = None  # ANTHROPIC_API_KEYS (or ANTHROPIC_API_KEY)

    def get_api_keys(self, provider: str) -> list[str]:
        """Get list of API keys for a provider."""
        key_map = {
            "gemini": self.gemini_api_keys,
            "groq": self.groq_api_keys,
            "claude": self.anthropic_api_keys,
        }
        keys_str = key_map.get(provider)
        if not keys_str:
            return []
        return [k.strip() for k in keys_str.split(",") if k.strip()]

    def get_providers(self) -> list[str]:
        """Get list of providers to try in order."""
        return [p.strip() for p in self.ai_provider.split(",") if p.strip()]

    # Default categories for products
    default_categories: list[str] = [
        "Canned Goods",
        "Cereals & Breakfast",
        "Snacks",
        "Baking & Cooking",
        "Condiments & Sauces",
        "Beverages",
        "Frozen",
        "Meat & Protein",
        "Dairy",
        "Produce",
        "Seasonings & Spices",
        "Pasta & Grains",
        "Other"
    ]

    # Low stock threshold (default quantity below which item is "low")
    low_stock_threshold: float = 1.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
