# collector/fetcher.py
import time
from datetime import datetime
from typing import Optional

import feedparser


def fetch_feed(url: str) -> list[dict]:
    """RSSフィードを取得して正規化した記事リストを返す。エラー時は空リスト。"""
    try:
        feed = feedparser.parse(url, request_headers={'User-Agent': 'Tech0-GiverBot/1.0'})
        return [a for a in (_normalize_entry(e, url) for e in feed.entries) if a]
    except Exception:
        return []


def _normalize_entry(entry, source_url: str) -> Optional[dict]:
    """feedparserエントリを標準dictに変換する。link/titleがない場合はNone。"""
    link = getattr(entry, 'link', None)
    title = getattr(entry, 'title', None)
    if not link or not title:
        return None

    published = None
    if getattr(entry, 'published_parsed', None):
        published = datetime(*entry.published_parsed[:6])
    elif getattr(entry, 'updated_parsed', None):
        published = datetime(*entry.updated_parsed[:6])
    else:
        published = datetime.now()

    summary = getattr(entry, 'summary', '') or ''

    return {
        'title': title.strip(),
        'url': link.strip(),
        'summary': summary[:500],
        'published': published,
        'source_url': source_url,
    }


def fetch_all_feeds(sources: list[dict], delay: float = 0.5) -> list[dict]:
    """全ソースのフィードを取得してソースメタデータを付与した記事リストを返す。"""
    all_articles = []
    for source in sources:
        articles = fetch_feed(source['url'])
        for article in articles:
            article['source_name'] = source['name']
            article['source_tier'] = source['tier']
            article['source_weight'] = source['weight']
        all_articles.extend(articles)
        time.sleep(delay)
    return all_articles
