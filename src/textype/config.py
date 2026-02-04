"""Configuration module for the Textype typing tutor application.

This module contains all configuration constants, lesson definitions, and
UI settings used throughout the application.
"""


# ============================================================================
# UI Configuration
# ============================================================================

SHOW_QWERTY: bool = False
"""Whether to show the QWERTY keyboard visualization by default."""

SHOW_FINGERS: bool = False
"""Whether to show the finger guide visualization by default."""

HARD_MODE: bool = True
"""Whether to enable hard mode (errors prevent progress)."""

SHOW_STATS_ON_END: bool = False
"""Whether to show statistics screen automatically after each drill."""

DRILL_DURATION: int = 300
"""Duration of each typing drill in seconds (5 minutes)."""

SHUFFLE_AFTER: int = 5
"""Number of repetitions before shuffling practice patterns."""


# Practice source configurations
# Sources: "local", "file", "api", "cmd", "ai"
SENTENCE_SOURCE: str = "api"
CODE_SOURCE: str = "local"

# Local File Paths
SENTENCES_FILE: str = "sentences.txt"
CODE_FILE: str = "snippets.py"

# Dynamic Commands and APIs
CODE_COMMAND: str = ""  # e.g., "grep -r 'def ' . | shuf -n 1"
QUOTE_API_URL: str = "https://api.quotify.top/random"
AI_ENDPOINT: str = "http://localhost:11434/api/generate"  # Ollama example
