import re

import requests
from bs4 import BeautifulSoup

ATCODER_BASE_URL = "https://atcoder.jp"


def fetch_problem_statement(contest_id: str) -> tuple[str, str]:
    """Fetch the problem statement text and title for an AHC contest.

    Args:
        contest_id: The contest ID (e.g. "ahc001").

    Returns:
        A tuple of (title, plain-text content of the task statement).

    Raises:
        requests.HTTPError: If the request fails.
        ValueError: If the task statement element is not found in the page.
    """
    url = f"{ATCODER_BASE_URL}/contests/{contest_id}/tasks/{contest_id}_a"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    task_statement = soup.find("div", id="task-statement")
    if task_statement is None:
        raise ValueError(
            f"Task statement element not found for contest '{contest_id}'. "
            f"URL: {url}"
        )
    
    title_tag = soup.title
    title = title_tag.text.replace(" | AtCoder", "").strip() if title_tag else contest_id
    title = re.sub(r"^[A-Z]\s*-\s*", "", title)

    return title, task_statement.get_text(separator="\n")
