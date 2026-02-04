"""Unit tests for the code_generator module."""

from unittest.mock import patch, MagicMock

import pytest
from textype.code_generator import generate_code_snippet, generate_code_snippet_async


class TestGenerateCodeSnippet:
    """Tests the generate_code_snippet function for various data sources."""

    @patch("textype.code_generator.subprocess.check_output")
    def test_generate_code_cmd_success(self, mock_check_output):
        """Tests successful code snippet generation from a command."""
        mock_check_output.return_value = b"code from command"

        config = {"CODE_SOURCE": "cmd", "CODE_COMMAND": "echo 'code'"}
        snippet = generate_code_snippet(config_overrides=config)

        assert snippet == "code from command"

    @patch(
        "textype.code_generator.subprocess.check_output",
        side_effect=Exception("Cmd Error"),
    )
    def test_generate_code_cmd_failure_fallback(self, mock_check_output):
        """Tests fallback to local snippets when a command fails."""
        config = {"CODE_SOURCE": "cmd", "CODE_COMMAND": "invalid-cmd"}
        snippet = generate_code_snippet(config_overrides=config)

        assert isinstance(snippet, str)
        assert len(snippet) > 0

    @patch("textype.code_generator.requests.post")
    def test_generate_code_ai_openai_success(self, mock_post):
        """Tests successful code snippet generation from the OpenAI API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "code from openai"}}]
        }
        mock_post.return_value = mock_response

        config = {
            "CODE_SOURCE": "ai",
            "AI_API_TYPE": "openai",
            "AI_ENDPOINT": "http://openai.api",
            "AI_MODEL": "gpt-4",
        }
        snippet = generate_code_snippet(language="python", config_overrides=config)

        assert snippet == "code from openai"

    @patch("textype.code_generator.requests.post")
    def test_generate_code_ai_ollama_success(self, mock_post):
        """Tests successful code snippet generation from the Ollama API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "code from ollama"}
        mock_post.return_value = mock_response

        config = {
            "CODE_SOURCE": "ai",
            "AI_API_TYPE": "ollama",
            "AI_ENDPOINT": "http://ollama.api",
            "AI_MODEL": "llama2",
        }
        snippet = generate_code_snippet(language="python", config_overrides=config)

        assert snippet == "code from ollama"

    @patch("textype.code_generator.requests.post", side_effect=Exception("AI Error"))
    def test_generate_code_ai_failure_fallback(self, mock_post):
        """Tests fallback to local snippets when the AI API fails."""
        config = {"CODE_SOURCE": "ai", "AI_ENDPOINT": "http://ai.api"}
        snippet = generate_code_snippet(config_overrides=config)

        assert isinstance(snippet, str)
        assert len(snippet) > 0

    @patch("textype.code_generator.Path.exists", return_value=True)
    @patch("builtins.open")
    def test_generate_code_file_success(self, mock_open, mock_exists):
        """Tests successful code snippet generation from a file."""
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "code from file"
        )

        config = {"CODE_SOURCE": "file", "CODE_FILE": "test.py"}
        snippet = generate_code_snippet(config_overrides=config)

        assert snippet == "code from file"

    @patch("textype.code_generator.Path.exists", return_value=False)
    def test_generate_code_file_not_found_fallback(self, mock_exists):
        """Tests fallback to local snippets when a file is not found."""
        config = {"CODE_SOURCE": "file", "CODE_FILE": "nonexistent.py"}
        snippet = generate_code_snippet(config_overrides=config)

        assert isinstance(snippet, str)
        assert len(snippet) > 0

    @pytest.mark.parametrize("language", ["python", "rust", "c", "cpp"])
    def test_generate_code_local_fallback(self, language):
        """Tests fallback to built-in snippets for each supported language."""
        config = {"CODE_SOURCE": "local"}
        snippet = generate_code_snippet(language=language, config_overrides=config)

        assert isinstance(snippet, str)
        assert len(snippet) > 0

    def test_unsupported_language_fallback(self):
        """Tests that an unsupported language falls back to Python snippets."""
        config = {"CODE_SOURCE": "local"}
        snippet = generate_code_snippet(language="java", config_overrides=config)

        # This will generate a python snippet as a fallback
        assert isinstance(snippet, str)
        assert len(snippet) > 0

    @pytest.mark.asyncio
    @patch("textype.code_generator.generate_code_snippet", return_value="async code")
    async def test_generate_code_snippet_async(self, mock_sync_generate):
        """Tests the asynchronous wrapper for code snippet generation."""
        snippet = await generate_code_snippet_async()
        assert snippet == "async code"
