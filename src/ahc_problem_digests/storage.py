import json
from pathlib import Path

DIGESTS_DIR = Path("digests")


def save_digest(contest_id: str, title: str, summary: str, digests_dir: Path = DIGESTS_DIR) -> Path:
    """Save a digest to a JSON file under *digests_dir*.

    Args:
        contest_id: The contest ID used as the file name stem.
        title: The problem title.
        summary: The summary text to save.
        digests_dir: Directory where digest files are stored. Defaults to
            ``digests/`` relative to the current working directory.

    Returns:
        The :class:`~pathlib.Path` of the written file.
    """
    digests_dir.mkdir(parents=True, exist_ok=True)
    digest = {"contest_id": contest_id, "title": title, "summary": summary}
    path = digests_dir / f"{contest_id}.json"
    path.write_text(json.dumps(digest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_digest(contest_id: str, digests_dir: Path = DIGESTS_DIR) -> dict | None:
    """Load a previously saved digest.

    Args:
        contest_id: The contest ID whose digest should be loaded.
        digests_dir: Directory where digest files are stored.

    Returns:
        A dictionary with ``contest_id`` and ``summary`` keys, or *None* if no
        digest has been saved for the given contest.
    """
    path = digests_dir / f"{contest_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
