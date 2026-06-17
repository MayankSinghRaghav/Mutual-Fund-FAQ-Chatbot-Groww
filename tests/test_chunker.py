import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Unit-level chunking logic (extracted from chunker.chunk to be testable)
# ---------------------------------------------------------------------------

CHUNK_SIZE = 500


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Pure function version of the chunking logic in ingest/chunker.py."""
    return [text[i: i + chunk_size] for i in range(0, len(text), chunk_size)]


def build_chunks(text: str, source: str, fund: str, chunk_size: int = CHUNK_SIZE) -> list[dict]:
    return [
        {"content": text[i: i + chunk_size], "source": source, "fund": fund}
        for i in range(0, len(text), chunk_size)
    ]


# ---------------------------------------------------------------------------
# Text extraction via BeautifulSoup (mirrors chunker behaviour)
# ---------------------------------------------------------------------------

def extract_text(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)


class TestChunkText:
    def test_short_text_yields_single_chunk(self):
        text = "A" * 100
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_text_exactly_chunk_size(self):
        text = "B" * 500
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 1

    def test_text_one_over_chunk_size(self):
        text = "C" * 501
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 2
        assert len(chunks[0]) == 500
        assert len(chunks[1]) == 1

    def test_multiple_chunks_correct_count(self):
        text = "D" * 1500
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 3

    def test_empty_text_yields_no_chunks(self):
        chunks = chunk_text("", chunk_size=500)
        assert chunks == []

    def test_chunk_boundaries_are_contiguous(self):
        text = "E" * 1200
        chunks = chunk_text(text, chunk_size=500)
        assert "".join(chunks) == text

    def test_unicode_text_chunked_by_character(self):
        text = "こんにちは" * 200  # Japanese characters
        chunks = chunk_text(text, chunk_size=500)
        assert "".join(chunks) == text


class TestBuildChunks:
    def test_chunk_dict_has_required_keys(self):
        chunks = build_chunks("Hello world " * 10, source="https://example.com", fund="HDFC Mid-Cap Fund")
        for chunk in chunks:
            assert "content" in chunk
            assert "source" in chunk
            assert "fund" in chunk

    def test_source_and_fund_propagated_to_all_chunks(self):
        text = "X" * 1200
        chunks = build_chunks(text, source="https://groww.in/test", fund="My Fund")
        for chunk in chunks:
            assert chunk["source"] == "https://groww.in/test"
            assert chunk["fund"] == "My Fund"

    def test_content_is_string(self):
        chunks = build_chunks("Sample text " * 50, source="http://a.com", fund="Fund A")
        for chunk in chunks:
            assert isinstance(chunk["content"], str)

    def test_no_content_loss(self):
        text = "Z" * 900
        chunks = build_chunks(text, source="http://b.com", fund="Fund B")
        assert "".join(c["content"] for c in chunks) == text


class TestHTMLExtraction:
    def test_strips_html_tags(self):
        html = "<html><body><p>Hello World</p></body></html>"
        text = extract_text(html)
        assert "<" not in text
        assert "Hello World" in text

    def test_extracts_nested_text(self):
        html = "<div><h1>Title</h1><p>Paragraph</p></div>"
        text = extract_text(html)
        assert "Title" in text
        assert "Paragraph" in text

    def test_empty_html_returns_empty(self):
        text = extract_text("<html><body></body></html>")
        assert text == ""

    def test_script_tags_text_is_included(self):
        # BeautifulSoup get_text includes script content; verify we get at least body text
        html = "<html><body><p>Content</p><script>var x=1;</script></body></html>"
        text = extract_text(html)
        assert "Content" in text
