import os
import pytest
from ahc_problem_digests.vote_aggregator import (
    escape_text,
    parse_problem_name,
    aggregate_votes,
    generate_markdown
)

def test_escape_text():
    # HTML escaping
    assert escape_text("<script>alert(1)</script>") == r"&lt;script&gt;alert\(1\)&lt;/script&gt;"
    assert escape_text("A & B") == r"A &amp; B"
    assert escape_text('"quotes"') == r"&quot;quotes&quot;"
    
    # Markdown escaping
    assert escape_text("*bold*") == r"\*bold\*"
    assert escape_text("_italic_") == r"\_italic\_"
    assert escape_text("[link](url)") == r"\[link\]\(url\)"
    assert escape_text("# Heading") == r"\# Heading"
    
    # Newlines
    assert escape_text("Line 1\nLine 2") == "Line 1<br>Line 2"

def test_parse_problem_name():
    # Normal format
    raw_name = "AHC062 - King's Tour - N×Nのグリッドで..."
    short_name, desc = parse_problem_name(raw_name)
    assert short_name == "AHC062 - King's Tour"
    assert desc == "N×Nのグリッドで..."
    
    # Missing description
    raw_name_2 = "AHC062 - King's Tour"
    short_name_2, desc_2 = parse_problem_name(raw_name_2)
    assert short_name_2 == raw_name_2
    assert desc_2 == ""

def test_aggregate_votes(tmp_path):
    csv_content = """タイムスタンプ,ニックネーム（匿名可）,問題名,理由
2026/04/17 10:00:54,alice,AHC062 - King's Tour - desc1,good
2026/04/18 10:35:42,bob,AHC011 - Sliding Tree - desc2,fun
2026/04/18 10:36:48,,AHC062 - King's Tour - desc1,
2026/04/18 10:49:20,charlie,AHC011 - Sliding Tree - desc2,great
2026/04/18 11:15:41,dave,AHC062 - King's Tour - desc1,nice
"""
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(csv_content, encoding="utf-8")
    
    results = aggregate_votes(str(csv_path))
    
    # AHC062 has 3 votes, AHC011 has 2 votes.
    assert len(results) == 2
    assert results[0]["count"] == 3
    assert results[0]["raw_name"] == "AHC062 - King's Tour - desc1"
    assert len(results[0]["comments"]) == 2  # one reason is empty
    assert results[0]["comments"][0]["nickname"] == "alice"
    assert results[0]["comments"][0]["reason"] == "good"
    assert results[0]["comments"][1]["nickname"] == "dave"
    
    assert results[1]["count"] == 2
    assert results[1]["raw_name"] == "AHC011 - Sliding Tree - desc2"

def test_generate_markdown():
    data = [
        {
            "count": 2,
            "raw_name": "AHC001 - Ad - desc1",
            "comments": [
                {"nickname": "alice", "reason": "fun"}
            ]
        }
    ]
    md = generate_markdown(data, "AHC_TEST")
    
    assert "title: AHC_TEST 投票結果" in md
    assert "| 1 | [AHC001 \\- Ad](#ahc001) | 2 |" in md
    assert '### <a id="ahc001"></a>AHC001 \\- Ad (2票)' in md
    assert "> desc1" in md
    assert "- **alice**: fun" in md
