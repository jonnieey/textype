import subprocess
import asyncio
import random
import requests

from pathlib import Path

from typing import Dict, Any, Optional
from textype.text_normalizer import normalize_text
from textype.curriculum import SENTENCES
import textype.config as config

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def generate_sentence(config_overrides: Optional[Dict[str, Any]] = None) -> str:
    """Generate a random practice sentence.

    Returns a random sentence from the configured sentence list.
    This is used for sentence practice mode.
    """

    # Helper to get config value
    def get(key):
        if config_overrides and key in config_overrides:
            return config_overrides[key]
        return getattr(config, key)

    source = get("SENTENCE_SOURCE")

    # 1. External API (Online)
    if source == "api" and HAS_REQUESTS:
        try:
            response = requests.get(get("QUOTE_API_URL"), timeout=2)
            if response.status_code == 200:
                # Adjust parsing based on specific API schema
                data = response.json()
                text = data.get("text", "")
                author = data.get("author")
                if author:
                    return normalize_text(f"{text}\n{author}")
                return normalize_text(text)
        except Exception:
            pass

    if source == "cmd" and get("CODE_COMMAND"):
        try:
            result = subprocess.check_output(get("CODE_COMMAND"), shell=True, timeout=2)
            return normalize_text(result.decode().strip())
        except Exception:
            pass

    if source == "ai" and HAS_REQUESTS:
        try:
            endpoint = get("AI_ENDPOINT")
            api_type = get("AI_API_TYPE")
            model = get("AI_MODEL")
            api_key = get("AI_API_KEY")

            # Auto-detect API type if set to "auto"
            if api_type == "auto":
                if "/chat/completions" in endpoint:
                    api_type = "openai"
                elif "/api/generate" in endpoint:
                    api_type = "ollama"
                else:
                    # Default to ollama for backward compatibility
                    api_type = "ollama"

            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            if api_type == "openai":
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Provide only sentences for typing practice. Do not include any explanations, commentary, or markdown formatting. Return only the sentences.",
                        }
                    ],
                    "max_tokens": 100,
                    "temperature": 0.7,
                }
            else:  # ollama
                payload = {
                    "model": model,
                    "prompt": "Provide only sentences for typing practice. Do not include any explanations, commentary, or markdown formatting. Return only the sentences.",
                    "stream": False,
                }

            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=10
            )
            if response.status_code == 200:
                if api_type == "openai":
                    result = (
                        response.json()
                        .get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                else:  # ollama
                    result = response.json().get("response", "")
                return normalize_text(result.strip())
        except Exception:
            pass

    if source == "file" or (source == "api" and get("SENTENCES_FILE")):
        if Path(get("SENTENCES_FILE")).exists():
            with open(get("SENTENCES_FILE"), "r") as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    return normalize_text(random.choice(lines))

    return normalize_text(random.choice(SENTENCES))


async def generate_sentence_async(
    config_overrides: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a random practice sentence asynchronously.

    Returns a random sentence from the configured sentence list.
    This is used for sentence practice mode with async pre-fetching.
    """
    # Run the synchronous function in a thread to avoid blocking
    return await asyncio.to_thread(generate_sentence, config_overrides)


if __name__ == "__main__":
    print(generate_sentence())
