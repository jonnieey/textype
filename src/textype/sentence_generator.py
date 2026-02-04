import subprocess
import asyncio
import random
import requests

from pathlib import Path

import textype.config as config
from textype.text_normalizer import normalize_text
from textype.curriculum import SENTENCES

# Optional dependencies
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def generate_sentence() -> str:
    """Generate a random practice sentence.

    Returns a random sentence from the configured sentence list.
    This is used for sentence practice mode.
    """

    source = config.SENTENCE_SOURCE

    # 1. External API (Online)
    if source == "api" and HAS_REQUESTS:
        try:
            response = requests.get(config.QUOTE_API_URL, timeout=2)
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

    if source == "cmd" and config.CODE_COMMAND:
        try:
            result = subprocess.check_output(config.CODE_COMMAND, shell=True, timeout=2)
            return normalize_text(result.decode().strip())
        except Exception:
            pass

    if source == "ai" and HAS_REQUESTS:
        try:
            payload = {
                "model": "codellama",
                "prompt": "Provide sentences for typing practice.",
                "stream": False,
            }
            response = requests.post(config.AI_ENDPOINT, json=payload, timeout=5)
            if response.status_code == 200:
                return normalize_text(response.json().get("response", "").strip())
        except Exception:
            pass

    if source == "file" or (source == "api" and config.SENTENCES_FILE):
        if Path(config.SENTENCES_FILE).exists():
            with open(config.SENTENCES_FILE, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    return normalize_text(random.choice(lines))

    # 3. Fallback: Static list in config.py
    return normalize_text(random.choice(SENTENCES))


async def generate_sentence_async() -> str:
    """Generate a random practice sentence asynchronously.

    Returns a random sentence from the configured sentence list.
    This is used for sentence practice mode with async pre-fetching.
    """
    # Run the synchronous function in a thread to avoid blocking
    return await asyncio.to_thread(generate_sentence)


if __name__ == "__main__":
    print(generate_sentence())
