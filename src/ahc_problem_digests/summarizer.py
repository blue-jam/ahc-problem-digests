import os

from google import genai

GEMINI_MODEL = "gemini-2.5-flash-lite"
SUMMARY_PROMPT_TEMPLATE = """\
以下のAtCoder Heuristic Contest (AHC) の問題文を140字程度の日本語で要約してください。
次の項目を簡潔にまとめてください。

- 問題の概要（何をする問題か）

---
{problem_text}
"""


def create_summary(problem_text: str, api_key: str | None = None) -> str:
    """Create a Japanese summary of an AHC problem statement using the Gemini API.

    Args:
        problem_text: The plain-text problem statement.
        api_key: Gemini API key. If *None*, the value of the ``GEMINI_API_KEY``
            environment variable is used.

    Returns:
        A Japanese summary string.

    Raises:
        ValueError: If no API key is available.
    """
    resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_key:
        raise ValueError(
            "Gemini API key is not set. "
            "Set the GEMINI_API_KEY environment variable or pass api_key explicitly."
        )

    client = genai.Client(api_key=resolved_key)
    prompt = SUMMARY_PROMPT_TEMPLATE.format(problem_text=problem_text)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text
