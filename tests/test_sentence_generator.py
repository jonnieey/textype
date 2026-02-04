"""Unit tests for the sentence_generator module."""

from unittest.mock import patch, MagicMock

import pytest
from textype.sentence_generator import generate_sentence, generate_sentence_async


class TestGenerateSentence:
    """Tests the generate_sentence function for various data sources."""

    @patch("textype.sentence_generator.requests.get")
    def test_generate_sentence_api_success(self, mock_get):
        """Tests successful sentence generation from an API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "A quote from API.", "author": "API"}
        mock_get.return_value = mock_response

        config = {"SENTENCE_SOURCE": "api", "QUOTE_API_URL": "http://test.api"}
        sentence = generate_sentence(config)

        assert "A quote from API." in sentence
        assert "API" in sentence
        mock_get.assert_called_once_with("http://test.api", timeout=2)

    @patch(
        "textype.sentence_generator.requests.get", side_effect=Exception("API Error")
    )
    @patch("textype.sentence_generator.random.choice")
    def test_generate_sentence_api_failure_fallback(self, mock_choice, mock_get):
        """Tests fallback to local sentences when the API fails."""
        mock_choice.return_value = "A local sentence."

        config = {"SENTENCE_SOURCE": "api", "QUOTE_API_URL": "http://test.api"}
        sentence = generate_sentence(config)

        assert sentence == "A local sentence."

    @patch("textype.sentence_generator.subprocess.check_output")
    def test_generate_sentence_cmd_success(self, mock_check_output):
        """Tests successful sentence generation from a command."""
        mock_check_output.return_value = b"Sentence from command."

        config = {"SENTENCE_SOURCE": "cmd", "CODE_COMMAND": "echo 'Sentence'"}
        sentence = generate_sentence(config)

        assert sentence == "Sentence from command."
        mock_check_output.assert_called_once_with(
            "echo 'Sentence'", shell=True, timeout=2
        )

    @patch(
        "textype.sentence_generator.subprocess.check_output",
        side_effect=Exception("Cmd Error"),
    )
    @patch("textype.sentence_generator.random.choice")
    def test_generate_sentence_cmd_failure_fallback(
        self, mock_choice, mock_check_output
    ):
        """Tests fallback to local sentences when a command fails."""
        mock_choice.return_value = "A local sentence."

        config = {"SENTENCE_SOURCE": "cmd", "CODE_COMMAND": "invalid-cmd"}
        sentence = generate_sentence(config)

        assert sentence == "A local sentence."

    @patch("textype.sentence_generator.Path.exists", return_value=True)
    @patch("builtins.open")
    def test_generate_sentence_file_success(self, mock_open, mock_exists):
        """Tests successful sentence generation from a file."""
        mock_open.return_value.__enter__.return_value = ["Sentence from file.\n"]

        config = {"SENTENCE_SOURCE": "file", "SENTENCES_FILE": "test.txt"}
        sentence = generate_sentence(config)

        assert sentence == "Sentence from file."

    @patch("textype.sentence_generator.Path.exists", return_value=False)
    @patch("textype.sentence_generator.random.choice")
    def test_generate_sentence_file_not_found_fallback(self, mock_choice, mock_exists):
        """Tests fallback to local sentences when a file is not found."""
        mock_choice.return_value = "A local sentence."

        config = {"SENTENCE_SOURCE": "file", "SENTENCES_FILE": "nonexistent.txt"}
        sentence = generate_sentence(config)

        assert sentence == "A local sentence."

    @patch("textype.sentence_generator.random.choice")
    def test_generate_sentence_local_default(self, mock_choice):
        """Tests default sentence generation from the local list."""
        mock_choice.return_value = "A local sentence."

        config = {"SENTENCE_SOURCE": "local"}
        sentence = generate_sentence(config)

        assert sentence == "A local sentence."

    @pytest.mark.asyncio
    @patch(
        "textype.sentence_generator.generate_sentence", return_value="Async sentence"
    )
    async def test_generate_sentence_async(self, mock_sync_generate):
        """Tests the asynchronous wrapper for sentence generation."""
        sentence = await generate_sentence_async()
        assert sentence == "Async sentence"

    @patch("textype.sentence_generator.requests.post")
    def test_generate_sentence_ai_openai_success(self, mock_post):
        """Tests successful sentence generation from the OpenAI API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Sentence from OpenAI."}}]
        }
        mock_post.return_value = mock_response

        config = {
            "SENTENCE_SOURCE": "ai",
            "AI_API_TYPE": "openai",
            "AI_ENDPOINT": "http://openai.api",
            "AI_MODEL": "gpt-4",
            "AI_API_KEY": "test-key",
        }
        sentence = generate_sentence(config)

        assert sentence == "Sentence from OpenAI."

    @patch("textype.sentence_generator.requests.post")
    def test_generate_sentence_ai_ollama_success(self, mock_post):
        """Tests successful sentence generation from the Ollama API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Sentence from Ollama."}
        mock_post.return_value = mock_response

        config = {
            "SENTENCE_SOURCE": "ai",
            "AI_API_TYPE": "ollama",
            "AI_ENDPOINT": "http://ollama.api",
            "AI_MODEL": "llama2",
        }
        sentence = generate_sentence(config)

        assert sentence == "Sentence from Ollama."

    @patch(
        "textype.sentence_generator.requests.post", side_effect=Exception("AI Error")
    )
    @patch("textype.sentence_generator.random.choice")
    def test_generate_sentence_ai_failure_fallback(self, mock_choice, mock_post):
        """Tests fallback to local sentences when the AI API fails."""
        mock_choice.return_value = "A local sentence."

        config = {"SENTENCE_SOURCE": "ai", "AI_ENDPOINT": "http://ai.api"}
        sentence = generate_sentence(config)

        assert sentence == "A local sentence."
