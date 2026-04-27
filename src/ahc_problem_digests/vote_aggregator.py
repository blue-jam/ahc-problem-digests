import csv
import html
import os
import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple

def escape_text(text: str) -> str:
    """Escape HTML and Markdown characters to prevent XSS and unintended formatting."""
    if not text:
        return ""
    # 1. HTML escape
    text = html.escape(text, quote=True)
    # 2. Markdown escape
    # Escape common markdown characters: \ ` * _ { } [ ] ( ) # + - . ! |
    # Note: don't escape & ; which are used in HTML entities like &lt;
    markdown_chars = r'([\\`*_{}\[\]()#+\-.!|])'
    text = re.sub(markdown_chars, r'\\\1', text)
    # Newlines should be converted to <br> or double spaces if we want them rendered,
    # but in our case, keeping them as literal strings might be better.
    # Let's replace actual newlines with `<br>` so they render nicely in list items.
    text = text.replace("\n", "<br>")
    return text

def parse_problem_name(raw_name: str) -> Tuple[str, str]:
    """Parse problem name like 'AHC062 - Title - Description' into ('AHC062 - Title', 'Description')."""
    parts = raw_name.split(" - ", 2)
    if len(parts) >= 2:
        short_name = f"{parts[0]} - {parts[1]}"
        description = parts[2] if len(parts) == 3 else ""
        return short_name, description
    return raw_name, ""

def aggregate_votes(csv_path: str) -> List[Dict[str, Any]]:
    """Read CSV and aggregate votes per problem."""
    results = defaultdict(lambda: {"count": 0, "comments": [], "raw_name": ""})
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            problem_name = row.get("問題名", "").strip()
            if not problem_name:
                continue
                
            nickname = row.get("ニックネーム（匿名可）", "").strip()
            reason = row.get("理由", "").strip()
            
            if not nickname:
                nickname = "名無しさん"
                
            results[problem_name]["count"] += 1
            results[problem_name]["raw_name"] = problem_name
            if reason:
                results[problem_name]["comments"].append({
                    "nickname": nickname,
                    "reason": reason
                })
                
    # Sort by count (descending), then by problem name (ascending)
    sorted_results = sorted(
        results.values(),
        key=lambda x: (-x["count"], x["raw_name"])
    )
    return sorted_results

def generate_markdown(aggregated_data: List[Dict[str, Any]], title: str) -> str:
    """Generate Markdown content for Jekyll."""
    lines = []
    
    # Front Matter
    lines.append("---")
    lines.append("layout: default")
    lines.append(f"title: {title} 投票結果")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title} 投票結果")
    lines.append("")
    
    # Ranking Table
    lines.append("## 順位表")
    lines.append("")
    lines.append("| 順位 | 問題 | 投票数 |")
    lines.append("| :--- | :--- | :--- |")
    
    current_rank = 1
    previous_count = -1
    for i, data in enumerate(aggregated_data):
        if data["count"] != previous_count:
            current_rank = i + 1
            previous_count = data["count"]
            
        short_name, _ = parse_problem_name(data["raw_name"])
        escaped_short_name = escape_text(short_name)
        # Markdown table doesn't like | in text, escape_text handles it
        lines.append(f"| {current_rank} | [{escaped_short_name}](#{short_name.split(' ')[0].lower()}) | {data['count']} |")
        
    lines.append("")
    
    # Details Section
    lines.append("## コメント一覧")
    lines.append("")
    
    for data in aggregated_data:
        short_name, description = parse_problem_name(data["raw_name"])
        escaped_short_name = escape_text(short_name)
        escaped_desc = escape_text(description)
        
        # Heading for the problem (use ID as HTML id for anchoring)
        problem_id = short_name.split(" ")[0].lower() if " " in short_name else short_name.lower()
        lines.append(f"### <a id=\"{problem_id}\"></a>[{escaped_short_name}](https://atcoder.jp/contests/{problem_id}) ({data['count']}票)")
        lines.append("")
        if escaped_desc:
            lines.append(f"> {escaped_desc}")
            lines.append("")
            
        if data["comments"]:
            for comment in data["comments"]:
                escaped_nick = escape_text(comment["nickname"])
                escaped_reason = escape_text(comment["reason"])
                lines.append(f"- **{escaped_nick}**: {escaped_reason}")
            lines.append("")
        else:
            lines.append("コメントはありません。")
            lines.append("")
            
    return "\n".join(lines)

def process_votes(target: str) -> None:
    """Main execution function."""
    csv_path = os.path.join("votes", f"{target}.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input file not found: {csv_path}")
        
    aggregated_data = aggregate_votes(csv_path)
    
    output_dir = os.path.join("docs", target)
    os.makedirs(output_dir, exist_ok=True)
    
    markdown_content = generate_markdown(aggregated_data, title=target.upper())
    output_path = os.path.join(output_dir, "index.md")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    print(f"Successfully generated {output_path}")
