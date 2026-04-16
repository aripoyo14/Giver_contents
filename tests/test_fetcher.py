# tests/test_fetcher.py
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest
from collector.fetcher import fetch_feed, fetch_all_feeds, _normalize_entry


def _make_entry(title="Test Title", link="https://example.com/article",
                summary="Test summary.", published_parsed=(2026, 4, 7, 8, 0, 0, 0, 97, 0)):
    entry = MagicMock()
    entry.title = title
    entry.link = link
    entry.summary = summary
    entry.published_parsed = published_parsed
    entry.updated_parsed = None
    return entry


def _make_feed(entries):
    feed = MagicMock()
    feed.entries = entries
    return feed


def test_fetch_feed_returns_normalized_articles():
    with patch('feedparser.parse', return_value=_make_feed([_make_entry()])):
        result = fetch_feed("https://example.com/feed")
    assert len(result) == 1
    assert result[0]['title'] == "Test Title"
    assert result[0]['url'] == "https://example.com/article"


def test_fetch_feed_returns_empty_list_on_exception():
    with patch('feedparser.parse', side_effect=Exception("Network error")):
        result = fetch_feed("https://example.com/feed")
    assert result == []


def test_normalize_entry_returns_none_when_link_missing():
    entry = MagicMock()
    entry.link = None
    entry.title = "Title"
    assert _normalize_entry(entry, "https://source.com") is None


def test_normalize_entry_returns_none_when_title_missing():
    entry = MagicMock()
    entry.link = "https://example.com"
    entry.title = None
    assert _normalize_entry(entry, "https://source.com") is None


def test_normalize_entry_uses_updated_when_published_missing():
    entry = _make_entry()
    entry.published_parsed = None
    entry.updated_parsed = (2026, 4, 6, 8, 0, 0, 0, 96, 0)
    result = _normalize_entry(entry, "https://source.com")
    assert result['published'] == datetime(2026, 4, 6, 8, 0, 0)


def test_fetch_all_feeds_adds_source_metadata():
    sources = [{"name": "TechCrunch AI", "url": "https://tc.com/feed", "tier": 1, "weight": 0.8}]
    with patch('feedparser.parse', return_value=_make_feed([_make_entry()])):
        with patch('time.sleep'):
            result = fetch_all_feeds(sources)
    assert result[0]['source_name'] == "TechCrunch AI"
    assert result[0]['source_tier'] == 1
    assert result[0]['source_weight'] == 0.8


def test_fetch_all_feeds_continues_on_single_feed_failure():
    sources = [
        {"name": "Good", "url": "https://good.com/feed", "tier": 1, "weight": 0.9},
        {"name": "Bad", "url": "https://bad.com/feed", "tier": 1, "weight": 0.9},
    ]
    def side_effect(url, **kwargs):
        if "bad" in url:
            raise Exception("timeout")
        return _make_feed([_make_entry()])

    with patch('feedparser.parse', side_effect=side_effect):
        with patch('time.sleep'):
            result = fetch_all_feeds(sources)
    assert len(result) == 1
    assert result[0]['source_name'] == "Good"
