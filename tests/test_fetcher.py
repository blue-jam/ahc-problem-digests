import pytest
import requests
from unittest.mock import MagicMock

from ahc_problem_digests.fetcher import fetch_problem_statement


def _make_html(task_statement_html: str, title: str = "A - Test Problem | AtCoder") -> str:
    return f"""
    <html>
    <head><title>{title}</title></head>
    <body>
      <div id="task-statement">{task_statement_html}</div>
    </body></html>
    """


def test_fetch_problem_statement_returns_text(mocker):
    """fetch_problem_statement returns the plain text of the task-statement div."""
    mock_response = MagicMock()
    mock_response.text = _make_html("<p>問題文のサンプル</p>")
    mock_response.raise_for_status = MagicMock()

    mocker.patch("ahc_problem_digests.fetcher.requests.get", return_value=mock_response)

    title, result = fetch_problem_statement("ahc001")

    assert title == "Test Problem"
    assert "問題文のサンプル" in result


def test_fetch_problem_statement_calls_correct_url(mocker):
    """fetch_problem_statement constructs the AtCoder URL from the contest ID."""
    mock_response = MagicMock()
    mock_response.text = _make_html("<p>test</p>")
    mock_response.raise_for_status = MagicMock()

    mock_get = mocker.patch(
        "ahc_problem_digests.fetcher.requests.get", return_value=mock_response
    )

    fetch_problem_statement("ahc042")

    called_url = mock_get.call_args[0][0]
    assert "ahc042" in called_url
    assert called_url.endswith("ahc042_a")


def test_fetch_problem_statement_raises_on_http_error(mocker):
    """fetch_problem_statement propagates HTTP errors."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")

    mocker.patch("ahc_problem_digests.fetcher.requests.get", return_value=mock_response)

    with pytest.raises(requests.HTTPError):
        fetch_problem_statement("ahc999")


def test_fetch_problem_statement_raises_when_element_missing(mocker):
    """fetch_problem_statement raises ValueError when task-statement div is absent."""
    mock_response = MagicMock()
    mock_response.text = "<html><body><p>No task statement here</p></body></html>"
    mock_response.raise_for_status = MagicMock()

    mocker.patch("ahc_problem_digests.fetcher.requests.get", return_value=mock_response)

    with pytest.raises(ValueError, match="Task statement element not found"):
        fetch_problem_statement("ahc001")
