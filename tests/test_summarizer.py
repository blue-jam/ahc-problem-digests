import pytest
from unittest.mock import MagicMock

from ahc_problem_digests.summarizer import create_summary


def test_create_summary_returns_text(mocker):
    """create_summary returns the text from the Gemini response."""
    mock_response = MagicMock()
    mock_response.text = "これは要約です。"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch(
        "ahc_problem_digests.summarizer.genai.Client",
        return_value=mock_client,
    )

    result = create_summary("問題文", api_key="dummy-key")

    assert result == "これは要約です。"


def test_create_summary_passes_problem_text_in_prompt(mocker):
    """create_summary embeds the problem text in the prompt sent to Gemini."""
    mock_response = MagicMock()
    mock_response.text = "要約"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch(
        "ahc_problem_digests.summarizer.genai.Client",
        return_value=mock_client,
    )

    create_summary("固有の問題文テキスト", api_key="dummy-key")

    call_kwargs = mock_client.models.generate_content.call_args
    prompt_arg = call_kwargs.kwargs.get("contents") or call_kwargs[0][0]
    assert "固有の問題文テキスト" in prompt_arg


def test_create_summary_uses_env_api_key(mocker, monkeypatch):
    """create_summary reads GEMINI_API_KEY from the environment when no key is passed."""
    monkeypatch.setenv("GEMINI_API_KEY", "env-api-key")

    mock_response = MagicMock()
    mock_response.text = "要約"
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    mock_client_cls = mocker.patch(
        "ahc_problem_digests.summarizer.genai.Client",
        return_value=mock_client,
    )

    create_summary("問題文")

    mock_client_cls.assert_called_once_with(api_key="env-api-key")


def test_create_summary_raises_without_api_key(mocker, monkeypatch):
    """create_summary raises ValueError when no API key is available."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        create_summary("問題文")
