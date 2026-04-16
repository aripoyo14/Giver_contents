# tests/test_writer.py
import tempfile
from datetime import datetime
from pathlib import Path
import pytest
from collector.writer import write_inbox


def _make_article(title="AI Changes Everything",
                   url="https://example.com/ai",
                   source_name="TechCrunch AI",
                   tier=1,
                   summary="A short summary."):
    return {
        'title': title,
        'url': url,
        'source_name': source_name,
        'source_tier': tier,
        'summary': summary,
        'published': datetime(2026, 4, 7, 8, 0, 0),
    }


def test_write_inbox_creates_markdown_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_inbox([_make_article()], output_dir=tmpdir)
        assert path.exists()
        assert path.suffix == '.md'


def test_write_inbox_filename_contains_today():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_inbox([_make_article()], output_dir=tmpdir)
        assert datetime.now().strftime("%Y-%m-%d") in path.name


def test_write_inbox_contains_article_title():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_inbox([_make_article(title="AI Changes Everything")], output_dir=tmpdir)
        assert "AI Changes Everything" in path.read_text(encoding='utf-8')


def test_write_inbox_contains_article_url():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_inbox([_make_article(url="https://example.com/special")], output_dir=tmpdir)
        assert "https://example.com/special" in path.read_text(encoding='utf-8')


def test_write_inbox_contains_source_tier():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_inbox([_make_article(tier=1)], output_dir=tmpdir)
        assert "Tier 1" in path.read_text(encoding='utf-8')


def test_write_inbox_creates_output_dir_if_not_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        new_dir = str(Path(tmpdir) / "new_inbox")
        path = write_inbox([_make_article()], output_dir=new_dir)
        assert path.exists()


def test_write_inbox_returns_path_object():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_inbox([_make_article()], output_dir=tmpdir)
        assert isinstance(path, Path)
