import pytest
from unittest.mock import MagicMock, patch


class TestGeneratorGroq:
    """Tests for the Groq provider path (no live API calls)."""

    def test_groq_generate_returns_string(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "The NAV is 42."

        with patch("runtime.generator.Groq") as MockGroq, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            MockGroq.return_value.chat.completions.create.return_value = mock_response
            from runtime.generator import Generator
            gen = Generator(provider="groq")
            result = gen.generate("What is the NAV?")

        assert result == "The NAV is 42."

    def test_groq_model_name_set_correctly(self):
        with patch("runtime.generator.Groq"), \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            from runtime.generator import Generator
            gen = Generator(provider="groq")
        assert gen.model_name == "llama-3.3-70b-versatile"

    def test_groq_generate_passes_prompt_as_user_message(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Answer"

        with patch("runtime.generator.Groq") as MockGroq, \
             patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
            mock_client = MockGroq.return_value
            mock_client.chat.completions.create.return_value = mock_response
            from runtime.generator import Generator
            gen = Generator(provider="groq")
            gen.generate("My prompt")

        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs[1]["messages"]
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "My prompt"


class TestGeneratorGemini:
    """Tests for the Gemini provider path (no live API calls)."""

    def test_gemini_raises_without_api_key(self):
        import os
        env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
        with patch("runtime.generator.genai"), \
             patch.dict("os.environ", env, clear=True):
            from runtime.generator import Generator
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                Generator(provider="gemini")

    def _make_model_mock(self, name: str) -> MagicMock:
        """MagicMock's `name` kwarg sets its repr, not .name — set it explicitly."""
        m = MagicMock()
        m.name = name
        m.supported_generation_methods = ["generateContent"]
        return m

    def test_gemini_generate_returns_text(self):
        mock_model = MagicMock()
        mock_model.generate_content.return_value = MagicMock(text="Gemini answer")

        with patch("runtime.generator.genai") as mock_genai, \
             patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):
            mock_genai.list_models.return_value = [
                self._make_model_mock("models/gemini-2.0-flash")
            ]
            mock_genai.GenerativeModel.return_value = mock_model
            from runtime.generator import Generator
            gen = Generator(provider="gemini")
            result = gen.generate("What is expense ratio?")

        assert result == "Gemini answer"

    def test_gemini_picks_priority_model(self):
        with patch("runtime.generator.genai") as mock_genai, \
             patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):
            mock_genai.list_models.return_value = [
                self._make_model_mock("models/gemini-1.5-flash"),
                self._make_model_mock("models/gemini-2.0-flash"),
            ]
            mock_genai.GenerativeModel.return_value = MagicMock()
            from runtime.generator import Generator
            gen = Generator(provider="gemini")

        assert gen.model_name == "models/gemini-2.0-flash"

    def test_gemini_falls_back_when_priority_models_unavailable(self):
        with patch("runtime.generator.genai") as mock_genai, \
             patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):
            mock_genai.list_models.return_value = [
                self._make_model_mock("models/gemini-unknown-v99"),
            ]
            mock_genai.GenerativeModel.return_value = MagicMock()
            from runtime.generator import Generator
            gen = Generator(provider="gemini")

        assert "gemini" in gen.model_name.lower()
