import pytest
from unittest.mock import MagicMock, patch


class TestRetriever:
    """Tests for runtime/retriever.py — all external dependencies are mocked."""

    def test_retrieve_returns_results_on_success(self):
        with patch("runtime.retriever.chromadb") as mock_chroma_mod, \
             patch("runtime.retriever.genai") as mock_genai, \
             patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):

            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "documents": [["Some fund text"]],
                "metadatas": [[{"source": "https://groww.in/test"}]],
            }
            mock_chroma_mod.PersistentClient.return_value.get_collection.return_value = mock_collection

            mock_genai.embed_content.return_value = {"embedding": [0.1, 0.2, 0.3]}

            from runtime.retriever import Retriever
            retriever = Retriever()
            result = retriever.retrieve("What is expense ratio?")

        assert result is not None
        assert "documents" in result

    def test_retrieve_returns_none_on_exception(self):
        with patch("runtime.retriever.chromadb") as mock_chroma_mod, \
             patch("runtime.retriever.genai") as mock_genai, \
             patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):

            mock_collection = MagicMock()
            mock_chroma_mod.PersistentClient.return_value.get_collection.return_value = mock_collection
            mock_genai.embed_content.side_effect = RuntimeError("Gemini API down")

            from runtime.retriever import Retriever
            retriever = Retriever()
            result = retriever.retrieve("query")

        assert result is None

    def test_retrieve_passes_query_embedding(self):
        with patch("runtime.retriever.chromadb") as mock_chroma_mod, \
             patch("runtime.retriever.genai") as mock_genai, \
             patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):

            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "documents": [["text"]],
                "metadatas": [[{"source": "url"}]],
            }
            mock_chroma_mod.PersistentClient.return_value.get_collection.return_value = mock_collection

            mock_genai.embed_content.return_value = {"embedding": [0.1, 0.2, 0.3]}

            from runtime.retriever import Retriever
            retriever = Retriever()
            retriever.retrieve("question")

            call_args = mock_collection.query.call_args
            query_emb = call_args[1]["query_embeddings"][0]
            assert query_emb == [0.1, 0.2, 0.3]

    def test_retrieve_uses_top_k(self):
        with patch("runtime.retriever.chromadb") as mock_chroma_mod, \
             patch("runtime.retriever.genai") as mock_genai, \
             patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):

            mock_collection = MagicMock()
            mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
            mock_chroma_mod.PersistentClient.return_value.get_collection.return_value = mock_collection

            mock_genai.embed_content.return_value = {"embedding": [0.1]}

            from runtime.retriever import Retriever
            retriever = Retriever()
            retriever.retrieve("query", top_k=5)

            call_args = mock_collection.query.call_args
            assert call_args[1]["n_results"] == 5

    def test_retrieve_default_top_k_is_3(self):
        with patch("runtime.retriever.chromadb") as mock_chroma_mod, \
             patch("runtime.retriever.genai") as mock_genai, \
             patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):

            mock_collection = MagicMock()
            mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
            mock_chroma_mod.PersistentClient.return_value.get_collection.return_value = mock_collection

            mock_genai.embed_content.return_value = {"embedding": [0.1]}

            from runtime.retriever import Retriever
            retriever = Retriever()
            retriever.retrieve("query")

            call_args = mock_collection.query.call_args
            assert call_args[1]["n_results"] == 3
