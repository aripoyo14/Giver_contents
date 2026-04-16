# collector/processor.py
from datetime import datetime, timedelta
from typing import Optional


def deduplicate(articles: list[dict]) -> list[dict]:
    """URLが重複する記事を除去し、最初に出現したものを残す。"""
    seen: set[str] = set()
    result = []
    for article in articles:
        url = article['url']
        if url not in seen:
            seen.add(url)
            result.append(article)
    return result


def filter_by_date(
    articles: list[dict],
    window_days: int = 14,
    reference_date: Optional[datetime] = None,
) -> list[dict]:
    """window_days以内に公開された記事のみを返す。"""
    if reference_date is None:
        reference_date = datetime.now()
    cutoff = reference_date - timedelta(days=window_days)
    return [a for a in articles if a.get('published') and a['published'] >= cutoff]


def sort_by_tier_and_date(articles: list[dict]) -> list[dict]:
    """Tier昇順（1が先）、同Tier内は公開日降順でソートする。"""
    return sorted(
        articles,
        key=lambda a: (a.get('source_tier', 2), -a['published'].timestamp()),
    )
