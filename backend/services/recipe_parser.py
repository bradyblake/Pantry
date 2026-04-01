import os
import json
import base64
import httpx
from pathlib import Path
from typing import Optional, List
import logging

from config import settings

logger = logging.getLogger(__name__)

# Try to import PDF libraries
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False


# Recipe extraction prompt (shared across providers)
RECIPE_PROMPT = """Analyze this recipe and extract the structured information. Return ONLY valid JSON with this structure:
{
  "name": "Recipe Name",
  "description": "Brief description of the dish",
  "prep_time_minutes": 15,
  "cook_time_minutes": 30,
  "servings": 4,
  "ingredients": [
    {"text": "1 lb ground beef", "quantity": 1, "unit": "lb", "item": "ground beef", "is_optional": false},
    {"text": "1 packet taco seasoning", "quantity": 1, "unit": "packet", "item": "taco seasoning", "is_optional": false},
    {"text": "Sour cream for serving (optional)", "quantity": null, "unit": null, "item": "sour cream", "is_optional": true}
  ],
  "instructions": "Step-by-step instructions as a single string with numbered steps",
  "tags": ["mexican", "quick", "kid-friendly"]
}

If multiple recipes are found, return an array of recipe objects.
If times or servings aren't specified, use null.
For ingredients, extract the quantity and unit when possible.

Return ONLY the JSON, no other text."""


class RateLimitError(Exception):
    """Raised when API rate limit is hit."""
    pass


class RecipeParser:
    """Parse recipes from PDFs and images using Gemini, Groq, or Claude APIs with automatic key rotation."""

    def __init__(self):
        self.providers = settings.get_providers()
        self.key_indices = {}  # Track current key index per provider

        # Initialize key indices
        for provider in ["gemini", "groq", "claude"]:
            self.key_indices[provider] = 0

    def _get_next_key(self, provider: str) -> Optional[str]:
        """Get the next API key for a provider, rotating through available keys."""
        keys = settings.get_api_keys(provider)
        if not keys:
            # Fallback to single key env vars
            fallback_vars = {
                "gemini": "GEMINI_API_KEY",
                "groq": "GROQ_API_KEY",
                "claude": "ANTHROPIC_API_KEY",
            }
            single_key = os.getenv(fallback_vars.get(provider, ""))
            return single_key if single_key else None

        # Get current key and rotate index
        idx = self.key_indices[provider] % len(keys)
        return keys[idx]

    def _rotate_key(self, provider: str):
        """Move to the next key for a provider."""
        self.key_indices[provider] += 1
        logger.info(f"Rotating to next {provider} API key (index {self.key_indices[provider]})")

    def extract_text_from_pdf(self, pdf_path: str) -> tuple[str, int]:
        """Extract text from PDF. Returns (text, page_count)."""
        if not HAS_PYMUPDF:
            raise ImportError("PyMuPDF (fitz) is required for PDF text extraction.")

        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n\n".join(text_parts), len(text_parts)

    def pdf_to_images(self, pdf_path: str, max_pages: int = 10) -> List[bytes]:
        """Convert PDF pages to images for vision API."""
        if HAS_PYMUPDF:
            doc = fitz.open(pdf_path)
            images = []
            for i, page in enumerate(doc):
                if i >= max_pages:
                    break
                mat = fitz.Matrix(150/72, 150/72)
                pix = page.get_pixmap(matrix=mat)
                images.append(pix.tobytes("png"))
            doc.close()
            return images
        elif HAS_PDF2IMAGE:
            pil_images = convert_from_path(pdf_path, first_page=1, last_page=max_pages, dpi=150)
            images = []
            for img in pil_images:
                import io
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                images.append(buf.getvalue())
            return images
        else:
            raise ImportError("Either PyMuPDF or pdf2image is required for PDF processing")

    def _parse_json_response(self, response_text: str) -> dict:
        """Extract and parse JSON from response text."""
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse response as JSON: {e}", "raw_response": response_text}

    # ==================== GEMINI ====================

    async def _gemini_request(self, payload: dict, api_key: str) -> dict:
        """Make a request to Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)

            if response.status_code == 429:
                raise RateLimitError("Gemini rate limit exceeded")
            if response.status_code in (401, 403):
                raise RateLimitError("Gemini auth error - invalid key")

            response.raise_for_status()
            data = response.json()

        return self._parse_json_response(data["candidates"][0]["content"]["parts"][0]["text"])

    async def _gemini_parse_text(self, text: str, api_key: str) -> dict:
        payload = {
            "contents": [{
                "parts": [{"text": RECIPE_PROMPT + "\n\nRecipe text:\n" + text}]
            }]
        }
        return await self._gemini_request(payload, api_key)

    async def _gemini_parse_image(self, image_data: bytes, media_type: str, api_key: str) -> dict:
        image_b64 = base64.standard_b64encode(image_data).decode("utf-8")
        payload = {
            "contents": [{
                "parts": [
                    {"inline_data": {"mime_type": media_type, "data": image_b64}},
                    {"text": RECIPE_PROMPT}
                ]
            }]
        }
        return await self._gemini_request(payload, api_key)

    # ==================== GROQ ====================

    async def _groq_request(self, payload: dict, api_key: str) -> dict:
        """Make a request to Groq API."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)

            if response.status_code == 429:
                raise RateLimitError("Groq rate limit exceeded")
            if response.status_code in (401, 403):
                raise RateLimitError("Groq auth error - invalid key")

            response.raise_for_status()
            data = response.json()

        return self._parse_json_response(data["choices"][0]["message"]["content"])

    async def _groq_parse_text(self, text: str, api_key: str) -> dict:
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": RECIPE_PROMPT + "\n\nRecipe text:\n" + text}],
            "max_tokens": 4096
        }
        return await self._groq_request(payload, api_key)

    async def _groq_parse_image(self, image_data: bytes, media_type: str, api_key: str) -> dict:
        image_b64 = base64.standard_b64encode(image_data).decode("utf-8")
        payload = {
            "model": "llama-3.2-90b-vision-preview",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_b64}"}},
                    {"type": "text", "text": RECIPE_PROMPT}
                ]
            }],
            "max_tokens": 4096
        }
        return await self._groq_request(payload, api_key)

    # ==================== CLAUDE ====================

    async def _claude_parse_text(self, text: str, api_key: str) -> dict:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": RECIPE_PROMPT + "\n\nRecipe text:\n" + text}]
            )
        except anthropic.RateLimitError:
            raise RateLimitError("Claude rate limit exceeded")
        except anthropic.AuthenticationError:
            raise RateLimitError("Claude auth error - invalid key")

        return self._parse_json_response(message.content[0].text)

    async def _claude_parse_image(self, image_data: bytes, media_type: str, api_key: str) -> dict:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        image_b64 = base64.standard_b64encode(image_data).decode("utf-8")

        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
                        {"type": "text", "text": RECIPE_PROMPT}
                    ]
                }]
            )
        except anthropic.RateLimitError:
            raise RateLimitError("Claude rate limit exceeded")
        except anthropic.AuthenticationError:
            raise RateLimitError("Claude auth error - invalid key")

        return self._parse_json_response(message.content[0].text)

    # ==================== PUBLIC METHODS WITH ROTATION ====================

    async def _try_with_rotation(self, provider: str, parse_func, *args) -> dict:
        """Try a parse function with key rotation on failure."""
        keys = settings.get_api_keys(provider)
        if not keys:
            # Try single key fallback
            fallback_vars = {"gemini": "GEMINI_API_KEY", "groq": "GROQ_API_KEY", "claude": "ANTHROPIC_API_KEY"}
            single_key = os.getenv(fallback_vars.get(provider, ""))
            if single_key:
                keys = [single_key]

        if not keys:
            raise ValueError(f"No API keys configured for {provider}")

        last_error = None
        attempts = len(keys)

        for _ in range(attempts):
            api_key = self._get_next_key(provider)
            if not api_key:
                break

            try:
                result = await parse_func(*args, api_key)
                return result
            except RateLimitError as e:
                logger.warning(f"{provider} key rate limited: {e}")
                last_error = e
                self._rotate_key(provider)
            except Exception as e:
                logger.error(f"{provider} request failed: {e}")
                last_error = e
                self._rotate_key(provider)

        raise last_error or ValueError(f"All {provider} keys exhausted")

    async def parse_recipe_from_text(self, text: str) -> dict:
        """Parse recipe from text, trying providers in order with key rotation."""
        last_error = None

        for provider in self.providers:
            try:
                if provider == "gemini":
                    return await self._try_with_rotation(provider, self._gemini_parse_text, text)
                elif provider == "groq":
                    return await self._try_with_rotation(provider, self._groq_parse_text, text)
                elif provider == "claude":
                    return await self._try_with_rotation(provider, self._claude_parse_text, text)
            except Exception as e:
                logger.warning(f"Provider {provider} failed, trying next: {e}")
                last_error = e
                continue

        raise last_error or ValueError("No AI providers configured")

    async def parse_recipe_from_image(self, image_data: bytes, media_type: str = "image/png") -> dict:
        """Parse recipe from image, trying providers in order with key rotation."""
        last_error = None

        for provider in self.providers:
            try:
                if provider == "gemini":
                    return await self._try_with_rotation(provider, self._gemini_parse_image, image_data, media_type)
                elif provider == "groq":
                    return await self._try_with_rotation(provider, self._groq_parse_image, image_data, media_type)
                elif provider == "claude":
                    return await self._try_with_rotation(provider, self._claude_parse_image, image_data, media_type)
            except Exception as e:
                logger.warning(f"Provider {provider} failed, trying next: {e}")
                last_error = e
                continue

        raise last_error or ValueError("No AI providers configured")

    async def parse_pdf(self, pdf_path: str, use_vision: bool = True) -> dict:
        """Parse recipes from a PDF file."""
        if use_vision:
            images = self.pdf_to_images(pdf_path, max_pages=5)
            all_recipes = []

            for i, img_data in enumerate(images):
                result = await self.parse_recipe_from_image(img_data)
                if isinstance(result, list):
                    all_recipes.extend(result)
                elif "error" not in result:
                    all_recipes.append(result)
                elif i == 0:
                    return result

            if len(all_recipes) == 1:
                return all_recipes[0]
            return all_recipes
        else:
            text, page_count = self.extract_text_from_pdf(pdf_path)
            return await self.parse_recipe_from_text(text)
