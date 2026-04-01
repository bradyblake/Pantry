import anthropic
import base64
from pathlib import Path
from config import ANTHROPIC_API_KEY

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client

PARSE_PROMPT = """Analyze this recipe image and extract the following information in JSON format:

{
  "title": "Recipe name",
  "description": "Brief description of the dish",
  "prep_time": 10,
  "cook_time": 30,
  "servings": 4,
  "ingredients": [
    {"name": "onion", "quantity": "1/2", "unit": "", "notes": "diced"},
    {"name": "flour", "quantity": "2", "unit": "cup", "notes": ""},
    {"name": "butter", "quantity": "1/4", "unit": "cup", "notes": "melted"},
    {"name": "eggs", "quantity": "3", "unit": "", "notes": ""}
  ],
  "instructions": "Step-by-step instructions as a single string, with steps separated by newlines",
  "tags": ["tag1", "tag2"],
  "source": "Source if visible (cookbook name, website, etc.)"
}

Rules:
- For quantity, use fractions exactly as written in cooking recipes: "1/2", "1/3", "1 1/4", "3/4", "2". Always a string. If no quantity, use "".
- For unit, use standard cooking measurements: cup, tbsp, tsp, oz, lb, g, kg, ml, L, clove, pinch, dash, can, etc.
- IMPORTANT: If there is no unit of measurement (like "1/2 onion", "3 eggs", "1 lemon"), leave unit as "" (empty string). Do NOT use "piece". The quantity + name is enough.
- Normalize ingredient names to lowercase (e.g., "Chicken Breast" -> "chicken breast").
- For tags, suggest categories like: breakfast, lunch, dinner, snack, dessert, vegetarian, vegan, gluten-free, quick, slow-cooker, etc.
- Return ONLY valid JSON, no markdown formatting or extra text."""


def parse_recipe_image(image_path: str) -> dict:
    """Send a recipe image to Claude Vision and get structured recipe data back."""
    path = Path(image_path)
    suffix = path.suffix.lower()

    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_type_map.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    message = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": PARSE_PROMPT,
                    },
                ],
            }
        ],
    )

    import json
    response_text = message.content[0].text

    # Handle possible markdown code blocks in response
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    return json.loads(response_text)
