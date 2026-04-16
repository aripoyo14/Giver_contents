# collector/writer.py
from datetime import datetime
from pathlib import Path


def write_inbox(articles: list[dict], output_dir: str = "inbox") -> Path:
    """記事リストを inbox/YYYY-MM-DD-articles.md に書き出してPathを返す。"""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = out / f"{date_str}-articles.md"

    lines = [
        f"# 収集記事 {date_str}\n\n",
        f"収集件数: {len(articles)}件\n\n---\n\n",
    ]
    for i, a in enumerate(articles, 1):
        published = a.get('published', datetime.now()).strftime("%Y-%m-%d %H:%M")
        lines += [
            f"## {i}. {a['title']}\n\n",
            f"- **ソース:** {a.get('source_name', '不明')}（Tier {a.get('source_tier', '?')}）\n",
            f"- **日時:** {published}\n",
            f"- **URL:** {a['url']}\n",
        ]
        if a.get('summary'):
            lines.append(f"- **概要:** {a['summary']}\n")
        lines.append("\n---\n\n")

    filepath.write_text(''.join(lines), encoding='utf-8')
    return filepath
