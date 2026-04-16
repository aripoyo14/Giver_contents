# tests/test_processor.py
from datetime import datetime, timedelta
import pytest
from collector.processor import deduplicate, filter_by_date, sort_by_tier_and_date


def _make_article(url="https://example.com/a", title="Title A",
                   tier=1, days_ago=1):
    return {
        'url': url,
        'title': title,
        'source_tier': tier,
        'source_weight': 0.8,
        'published': datetime(2026, 4, 7) - timedelta(days=days_ago),
    }


REF = datetime(2026, 4, 7)


def test_deduplicate_removes_same_url():
    articles = [
        _make_article(url="https://example.com/a"),
        _make_article(url="https://example.com/a"),
        _make_article(url="https://example.com/b"),
    ]
    assert len(deduplicate(articles)) == 2


def test_deduplicate_keeps_first_occurrence():
    articles = [
        _make_article(url="https://example.com/a", title="First"),
        _make_article(url="https://example.com/a", title="Second"),
    ]
    assert deduplicate(articles)[0]['title'] == "First"


def test_deduplicate_returns_empty_for_empty_input():
    assert deduplicate([]) == []


def test_filter_by_date_removes_articles_outside_window():
    articles = [
        {**_make_article(url="https://example.com/new"), 'published': REF - timedelta(days=5)},
        {**_make_article(url="https://example.com/old"), 'published': REF - timedelta(days=20)},
    ]
    result = filter_by_date(articles, window_days=14, reference_date=REF)
    assert len(result) == 1
    assert result[0]['url'] == "https://example.com/new"


def test_filter_by_date_keeps_boundary_article():
    articles = [{**_make_article(), 'published': REF - timedelta(days=14)}]
    assert len(filter_by_date(articles, window_days=14, reference_date=REF)) == 1


def test_filter_by_date_uses_now_when_reference_not_given():
    articles = [{**_make_article(), 'published': datetime.now() - timedelta(days=1)}]
    assert len(filter_by_date(articles, window_days=14)) == 1


def test_sort_puts_tier1_before_tier2():
    articles = [
        _make_article(url="https://example.com/t2", tier=2),
        _make_article(url="https://example.com/t1", tier=1),
    ]
    result = sort_by_tier_and_date(articles)
    assert result[0]['source_tier'] == 1


def test_sort_within_same_tier_newer_first():
    articles = [
        {**_make_article(url="https://example.com/old", tier=1), 'published': REF - timedelta(days=5)},
        {**_make_article(url="https://example.com/new", tier=1), 'published': REF - timedelta(days=1)},
    ]
    result = sort_by_tier_and_date(articles)
    assert result[0]['url'] == "https://example.com/new"
