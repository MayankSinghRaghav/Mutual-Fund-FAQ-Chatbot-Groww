import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


def make_app(retriever, generator):
    """Build the FastAPI app with injected mocks (avoids importing live singletons).

    Patches are active during the initial import so the module-level Retriever()
    and Generator() calls don't hit real ChromaDB or Groq. After import the
    module is cached, so subsequent calls only swap the singleton references.
    """
    with patch("runtime.retriever.chromadb"), \
         patch("runtime.retriever.genai"), \
         patch("runtime.generator.Groq"), \
         patch.dict("os.environ", {"GEMINI_API_KEY": "t", "GROQ_API_KEY": "t"}):

        import runtime.phase_9_api.main as api_mod

        api_mod.retriever = retriever
        api_mod.generator = generator

        return TestClient(api_mod.app)


# ---------------------------------------------------------------------------
# /chat endpoint — happy path
# ---------------------------------------------------------------------------

class TestChatEndpointHappyPath:
    def test_returns_200_for_valid_query(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        response = client.post("/chat", json={"query": "What is the expense ratio?"})
        assert response.status_code == 200

    def test_response_has_answer_and_sources(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        data = client.post("/chat", json={"query": "What is the NAV?"}).json()
        assert "answer" in data
        assert "sources" in data

    def test_answer_is_string(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        data = client.post("/chat", json={"query": "Tell me about HDFC Mid-Cap."}).json()
        assert isinstance(data["answer"], str)

    def test_sources_is_list(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        data = client.post("/chat", json={"query": "What is the fund category?"}).json()
        assert isinstance(data["sources"], list)

    def test_sources_deduplication(self, mock_retriever, mock_generator):
        """Duplicate source URLs should be collapsed into one."""
        mock_retriever.retrieve.return_value = {
            "documents": [["text1", "text2"]],
            "metadatas": [[
                {"source": "https://groww.in/hdfc"},
                {"source": "https://groww.in/hdfc"},
            ]],
        }
        client = make_app(mock_retriever, mock_generator)
        data = client.post("/chat", json={"query": "NAV?"}).json()
        assert len(data["sources"]) == 1


# ---------------------------------------------------------------------------
# /chat endpoint — safety filter
# ---------------------------------------------------------------------------

class TestChatEndpointSafetyFilter:
    def test_advisory_query_blocked_with_200(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        response = client.post("/chat", json={"query": "Should I invest in HDFC?"})
        assert response.status_code == 200

    def test_advisory_query_returns_refusal_message(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        data = client.post("/chat", json={"query": "should i invest here"}).json()
        assert "cannot provide investment advice" in data["answer"].lower() or \
               "factual information" in data["answer"].lower()

    def test_advisory_query_has_empty_sources(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        data = client.post("/chat", json={"query": "give me advice"}).json()
        assert data["sources"] == []

    def test_pii_query_blocked(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        data = client.post("/chat", json={"query": "My PAN is ABCDE1234F"}).json()
        assert data["sources"] == []

    def test_retriever_not_called_when_unsafe(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        client.post("/chat", json={"query": "should i invest?"})
        mock_retriever.retrieve.assert_not_called()

    def test_generator_not_called_when_unsafe(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        client.post("/chat", json={"query": "should i invest?"})
        mock_generator.generate.assert_not_called()


# ---------------------------------------------------------------------------
# /chat endpoint — empty / no results from retriever
# ---------------------------------------------------------------------------

class TestChatEndpointEmptyRetrieval:
    def test_no_results_returns_fallback_message(self, empty_retriever, mock_generator):
        client = make_app(empty_retriever, mock_generator)
        data = client.post("/chat", json={"query": "What is Nifty 50?"}).json()
        assert "couldn't find" in data["answer"].lower()

    def test_none_results_returns_fallback_message(self, none_retriever, mock_generator):
        client = make_app(none_retriever, mock_generator)
        data = client.post("/chat", json={"query": "What is Nifty 50?"}).json()
        assert "couldn't find" in data["answer"].lower()

    def test_generator_not_called_when_no_results(self, empty_retriever, mock_generator):
        client = make_app(empty_retriever, mock_generator)
        client.post("/chat", json={"query": "Something obscure"})
        mock_generator.generate.assert_not_called()


# ---------------------------------------------------------------------------
# /chat endpoint — request validation
# ---------------------------------------------------------------------------

class TestChatEndpointValidation:
    def test_missing_query_field_returns_422(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        response = client.post("/chat", json={})
        assert response.status_code == 422

    def test_empty_body_returns_422(self, mock_retriever, mock_generator):
        client = make_app(mock_retriever, mock_generator)
        response = client.post("/chat", content=b"", headers={"content-type": "application/json"})
        assert response.status_code == 422
