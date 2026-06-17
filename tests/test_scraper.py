import pytest
from unittest.mock import patch, MagicMock, mock_open, call
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers that mirror ingest/scraper.py logic (pure functions extracted)
# ---------------------------------------------------------------------------

def scrape_url(name: str, url: str, session) -> tuple[bool, str | None]:
    """Returns (success, html_content_or_None)."""
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            return True, response.text
        return False, None
    except Exception:
        return False, None


def filename_for(name: str) -> str:
    return f"{name.replace(' ', '_')}.html"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestScrapeUrl:
    def test_successful_fetch_returns_true_and_html(self):
        mock_session = MagicMock()
        mock_session.get.return_value = MagicMock(status_code=200, text="<html>content</html>")
        success, html = scrape_url("HDFC Mid-Cap Fund", "https://example.com", mock_session)
        assert success is True
        assert html == "<html>content</html>"

    def test_404_response_returns_false(self):
        mock_session = MagicMock()
        mock_session.get.return_value = MagicMock(status_code=404, text="")
        success, html = scrape_url("HDFC Fund", "https://example.com", mock_session)
        assert success is False
        assert html is None

    def test_500_response_returns_false(self):
        mock_session = MagicMock()
        mock_session.get.return_value = MagicMock(status_code=500, text="")
        success, html = scrape_url("HDFC Fund", "https://example.com", mock_session)
        assert success is False

    def test_connection_error_returns_false(self):
        mock_session = MagicMock()
        mock_session.get.side_effect = ConnectionError("Network failure")
        success, html = scrape_url("HDFC Fund", "https://example.com", mock_session)
        assert success is False
        assert html is None

    def test_timeout_returns_false(self):
        import requests
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.Timeout()
        success, html = scrape_url("HDFC Fund", "https://example.com", mock_session)
        assert success is False

    def test_get_called_with_correct_url_and_timeout(self):
        mock_session = MagicMock()
        mock_session.get.return_value = MagicMock(status_code=200, text="html")
        scrape_url("Fund", "https://target.com/path", mock_session)
        mock_session.get.assert_called_once_with("https://target.com/path", timeout=10)


class TestFilenameFor:
    def test_spaces_replaced_with_underscores(self):
        assert filename_for("HDFC Mid-Cap Fund") == "HDFC_Mid-Cap_Fund.html"

    def test_single_word_name(self):
        assert filename_for("HDFC") == "HDFC.html"

    def test_multiple_spaces(self):
        assert filename_for("A B C") == "A_B_C.html"

    def test_html_extension_present(self):
        name = "Some Fund Name"
        assert filename_for(name).endswith(".html")
