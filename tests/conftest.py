import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest


@pytest.fixture
def mock_retriever():
    """A retriever that returns one document with metadata."""
    retriever = MagicMock()
    retriever.retrieve.return_value = {
        "documents": [["HDFC Mid-Cap Fund has an expense ratio of 0.75%."]],
        "metadatas": [[{"source": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"}]],
    }
    return retriever


@pytest.fixture
def empty_retriever():
    """A retriever that returns no results."""
    retriever = MagicMock()
    retriever.retrieve.return_value = {"documents": [[]], "metadatas": [[]]}
    return retriever


@pytest.fixture
def none_retriever():
    """A retriever that returns None (e.g. ChromaDB unavailable)."""
    retriever = MagicMock()
    retriever.retrieve.return_value = None
    return retriever


@pytest.fixture
def mock_generator():
    """A generator that returns a fixed answer."""
    generator = MagicMock()
    generator.generate.return_value = "The expense ratio is 0.75%."
    return generator
