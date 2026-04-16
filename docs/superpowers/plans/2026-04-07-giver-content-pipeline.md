# Giver コンテンツ配信パイプライン 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** テック/AIニュースを自動収集・整形し、Tech0 LINE向けGiverコンテンツのドラフトをGitHub PRとして生成するパイプラインを構築する。

**Architecture:** PythonスクリプトがRSSフィードを収集して `inbox/` にMarkdownで保存。Claude Codeカスタムコマンド `tech0-giver-draft` が記事を選別・スコアリングしてLINE文面を生成、`drafts/` に保存してGitHub PRを作成。レビュー・承認はGitHub PR上で行い、承認後に担当者がLINEへ手動配信する。

**Tech Stack:** Python 3.11+, feedparser 6.x, pytest, gh CLI（GitHub CLI）, Claude Code カスタムコマンド

---

## ファイル構成

```
Tech0/Marketing/Giverコンテンツ/
├── collector/
│   ├── __init__.py          # パッケージ定義
│   ├── sources.py           # RSSソース設定（Tier 1 / Tier 2）
│   ├── fetcher.py           # RSSフェッチ・エントリ正規化
│   ├── processor.py         # 重複除去・日付フィルター・ソート
│   └── writer.py            # inbox/ への Markdown 書き出し
├── tests/
│   ├── __init__.py
│   ├── test_fetcher.py
│   ├── test_processor.py
│   └── test_writer.py
├── inbox/                   # Collector の出力先（YYYY-MM-DD-articles.md）
│   └── .gitkeep
├── drafts/                  # tech0-giver-draft の出力先（YYYY-MM-DD.md）
│   └── .gitkeep
├── logs/                    # Cron ログ
│   └── .gitkeep
├── .claude/
│   └── commands/
│       └── tech0-giver-draft.md  # Claude Code カスタムコマンド
├── run_collector.py         # エントリーポイント
├── requirements.txt
└── .gitignore
```

---

## Task 1: プロジェクトセットアップ

**Files:**
- Create: `Tech0/Marketing/Giverコンテンツ/requirements.txt`
- Create: `Tech0/Marketing/Giverコンテンツ/.gitignore`
- Create: `Tech0/Marketing/Giverコンテンツ/collector/__init__.py`
- Create: `Tech0/Marketing/Giverコンテンツ/tests/__init__.py`
- Create: `Tech0/Marketing/Giverコンテンツ/inbox/.gitkeep`
- Create: `Tech0/Marketing/Giverコンテンツ/drafts/.gitkeep`
- Create: `Tech0/Marketing/Giverコンテンツ/logs/.gitkeep`

- [ ] **Step 1: Git リポジトリを初期化する**

```bash
cd "/Users/shunsuke_arimura/Desktop/projects/Tech0/Marketing/Giverコンテンツ"
git init
```

- [ ] **Step 2: requirements.txt を作成する**

```
feedparser==6.0.11
requests==2.31.0
beautifulsoup4==4.12.3
python-dateutil==2.9.0
pytest==8.1.0
pytest-cov==5.0.0
```

- [ ] **Step 3: .gitignore を作成する**

```
__pycache__/
*.pyc
.venv/
venv/
.env
logs/*.log
inbox/*.md
```

> Note: `inbox/` は収集した生データのため gitignore。`drafts/` はレビュー対象のため追跡する。

- [ ] **Step 4: パッケージの `__init__.py` を作成する**

`collector/__init__.py` と `tests/__init__.py` は空ファイルで作成。

```bash
touch collector/__init__.py tests/__init__.py
```

- [ ] **Step 5: ディレクトリと .gitkeep を作成する**

```bash
mkdir -p inbox drafts logs .claude/commands
touch inbox/.gitkeep drafts/.gitkeep logs/.gitkeep
```

- [ ] **Step 6: 仮想環境を作成して依存パッケージをインストールする**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Expected: `Successfully installed feedparser-6.0.11 ...` などが表示される。

- [ ] **Step 7: コミットする**

```bash
git add requirements.txt .gitignore collector/__init__.py tests/__init__.py inbox/.gitkeep drafts/.gitkeep logs/.gitkeep
git commit -m "chore: プロジェクト初期セットアップ"
```

---

## Task 2: ソース設定

**Files:**
- Create: `collector/sources.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_sources.py` を作成:

```python
from collector.sources import SOURCES, ALL_SOURCES


def test_sources_have_required_fields():
    for source in SOURCES:
        assert 'name' in source
        assert 'url' in source
        assert source['tier'] == 1
        assert 0 < source['weight'] <= 1.0


def test_all_sources_are_tier1():
    tiers = {s['tier'] for s in ALL_SOURCES}
    assert tiers == {1}


def test_has_at_least_three_sources():
    assert len(SOURCES) >= 3
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_sources.py -v
```

Expected: `ModuleNotFoundError: No module named 'collector.sources'`

- [ ] **Step 3: sources.py を実装する**

```python
# collector/sources.py
# Tier 1: 公式一次情報・編集部ありの信頼性の高いメディアのみ
# ユーザー生成コンテンツはプロンプトインジェクションリスクのため除外

SOURCES = [
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/news/rss.xml",
        "tier": 1,
        "weight": 1.0,
        "language": "en",
    },
    {
        "name": "Google DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "tier": 1,
        "weight": 0.9,
        "language": "en",
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "tier": 1,
        "weight": 0.9,
        "language": "en",
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "tier": 1,
        "weight": 0.8,
        "language": "en",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "tier": 1,
        "weight": 0.8,
        "language": "en",
    },
    {
        "name": "ITmedia AI+",
        "url": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
        "tier": 1,
        "weight": 0.8,
        "language": "ja",
    },
]

ALL_SOURCES = SOURCES
```

> ⚠️ RSS URLはサービス側の変更で無効になる場合がある。Task 9の統合テストで実際にアクセスして確認すること。

- [ ] **Step 4: テストがパスすることを確認する**

```bash
pytest tests/test_sources.py -v
```

Expected: `4 passed`

- [ ] **Step 5: コミットする**

```bash
git add collector/sources.py tests/test_sources.py
git commit -m "feat: RSSソース設定を追加"
```

---

## Task 3: RSS フェッチャー（TDD）

**Files:**
- Create: `collector/fetcher.py`
- Create: `tests/test_fetcher.py`

- [ ] **Step 1: 失敗するテストを書く**

```python
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
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_fetcher.py -v
```

Expected: `ImportError: cannot import name 'fetch_feed' from 'collector.fetcher'`

- [ ] **Step 3: fetcher.py を実装する**

```python
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
```

- [ ] **Step 4: テストがパスすることを確認する**

```bash
pytest tests/test_fetcher.py -v
```

Expected: `8 passed`

- [ ] **Step 5: コミットする**

```bash
git add collector/fetcher.py tests/test_fetcher.py
git commit -m "feat: RSSフェッチャーを実装"
```

---

## Task 4: 記事プロセッサー（TDD）

**Files:**
- Create: `collector/processor.py`
- Create: `tests/test_processor.py`

- [ ] **Step 1: 失敗するテストを書く**

```python
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
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_processor.py -v
```

Expected: `ImportError: cannot import name 'deduplicate' from 'collector.processor'`

- [ ] **Step 3: processor.py を実装する**

```python
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
```

- [ ] **Step 4: テストがパスすることを確認する**

```bash
pytest tests/test_processor.py -v
```

Expected: `9 passed`

- [ ] **Step 5: コミットする**

```bash
git add collector/processor.py tests/test_processor.py
git commit -m "feat: 記事プロセッサー（重複除去・フィルター・ソート）を実装"
```

---

## Task 5: Inboxライター（TDD）

**Files:**
- Create: `collector/writer.py`
- Create: `tests/test_writer.py`

- [ ] **Step 1: 失敗するテストを書く**

```python
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
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_writer.py -v
```

Expected: `ImportError: cannot import name 'write_inbox' from 'collector.writer'`

- [ ] **Step 3: writer.py を実装する**

```python
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
```

- [ ] **Step 4: テストがパスすることを確認する**

```bash
pytest tests/test_writer.py -v
```

Expected: `7 passed`

- [ ] **Step 5: 全テストが通ることを確認する**

```bash
pytest --cov=collector --cov-report=term-missing
```

Expected: coverage 80%以上

- [ ] **Step 6: コミットする**

```bash
git add collector/writer.py tests/test_writer.py
git commit -m "feat: Inboxライターを実装"
```

---

## Task 6: メインランナー

**Files:**
- Create: `run_collector.py`

- [ ] **Step 1: run_collector.py を作成する**

```python
#!/usr/bin/env python3
"""毎朝8時にCronから実行するエントリーポイント。"""
import sys
from collector.sources import ALL_SOURCES
from collector.fetcher import fetch_all_feeds
from collector.processor import deduplicate, filter_by_date, sort_by_tier_and_date
from collector.writer import write_inbox


def main() -> int:
    print("📡 記事収集を開始します...")

    articles = fetch_all_feeds(ALL_SOURCES)
    print(f"  取得: {len(articles)}件")

    articles = deduplicate(articles)
    print(f"  重複除去後: {len(articles)}件")

    articles = filter_by_date(articles, window_days=14)
    print(f"  2週間フィルター後: {len(articles)}件")

    articles = sort_by_tier_and_date(articles)

    output_path = write_inbox(articles)
    print(f"✅ 保存完了: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 手動実行して動作確認する**

```bash
cd "/Users/shunsuke_arimura/Desktop/projects/Tech0/Marketing/Giverコンテンツ"
source .venv/bin/activate
python run_collector.py
```

Expected:
```
📡 記事収集を開始します...
  取得: XX件
  重複除去後: XX件
  2週間フィルター後: XX件
✅ 保存完了: inbox/2026-04-07-articles.md
```

> ⚠️ RSSフィードがアクセスできない場合（URLが変わった等）は0件になる。`inbox/YYYY-MM-DD-articles.md` を開いて内容を確認し、必要なら `collector/sources.py` のURLを修正する。

- [ ] **Step 3: コミットする**

```bash
git add run_collector.py
git commit -m "feat: メインランナーを追加"
```

---

## Task 7: tech0-giver-draft カスタムコマンド

**Files:**
- Create: `.claude/commands/tech0-giver-draft.md`

- [ ] **Step 1: .claude/commands/ ディレクトリを確認する**

```bash
ls .claude/commands/
```

- [ ] **Step 2: tech0-giver-draft.md を作成する**

```markdown
# tech0-giver-draft

Tech0 Giverコンテンツ用のLINEドラフトを `inbox/` の最新記事から生成する。

## 実行手順

### Step 1: 最新の収集記事を読む

`inbox/` フォルダ内で最新の `YYYY-MM-DD-articles.md` を見つけて全文を読む。

### Step 2: 各記事をスコアリングする

以下の4軸で各記事を0〜10で採点し、合計スコアを算出する。

| 軸 | 採点基準 |
|---|---|
| 学習価値 | 「これを知ると何かできるようになる」感があるか |
| 生活・仕事直結度 | 読者の仕事や日常と関係あるか（自分ごと化できるか） |
| 発見価値 | Tech0ペルソナにとって初めて知る価値があるか |
| 初学者親和性 | 技術用語なしで噛み砕いて説明できる内容か |

**除外する記事:**
- 専門家向けすぎて初学者に届かないもの（論文・実装詳細系）
- 学びに繋がらないゴシップ・炎上系
- Tier 2（Qiita/Zenn）の記事は文体参考のみ、採用しない

### Step 3: 上位3件のLINE文面を生成する

**ペルソナ（対象読者）:**
- Tech0の説明会・イベントに参加してLINE登録済みの20〜35歳社会人/学生
- ChatGPT程度の知識。技術用語は苦手
- 「学ぶべきか迷っている」「背中を押してほしい」状態

**LINE文面フォーマット（厳守）:**
```
【今日のテック/AIニュース】

📌 [トピック名：15文字以内・キャッチー]

[何が起きたか：2〜3行、平易な言葉・技術用語なし]

💡 あなたへの影響：[1行、仕事や日常との具体的な関連]

#Tech0 #AI #テクノロジー
```

### Step 4: drafts/ に保存する

`drafts/YYYY-MM-DD.md` を以下の形式で作成する（日付は今日）:

```markdown
# LINE Giverコンテンツ案 YYYY-MM-DD

> 生成日時: YYYY-MM-DD HH:MM
> 収集ソース: inbox/YYYY-MM-DD-articles.md

---

## 案1（スコア: XX/40）
**元記事:** [タイトル](URL)
**選定理由:** [学習価値・生活直結度などを一言で]

[LINE文面]

---

## 案2（スコア: XX/40）
...

---

## 案3（スコア: XX/40）
...
```

### Step 5: GitHubにコミットしてPRを作成する

```bash
git add drafts/YYYY-MM-DD.md
git commit -m "draft: YYYY-MM-DD のLINEコンテンツ案"
gh pr create \
  --title "[DRAFT] YYYY-MM-DD Giver LINE コンテンツ案" \
  --body "## 概要
本日分のLINE Giverコンテンツ案（3件）を生成しました。

## レビュー依頼
- [ ] 文面・トーンの確認
- [ ] 採用する案の選択
- [ ] 必要に応じて文面を編集
- [ ] 承認後、LINEへ手動配信

## 元記事
各案の元記事URLはdrafts/YYYY-MM-DD.mdを参照"
```
```

- [ ] **Step 3: コマンドが Claude Code から呼び出せることを確認する**

Claude Code 上で `/tech0-giver-draft` と入力し、コマンドが認識されることを確認する。

- [ ] **Step 4: コミットする**

```bash
git add .claude/commands/tech0-giver-draft.md
git commit -m "feat: tech0-giver-draft カスタムコマンドを追加"
```

---

## Task 8: Cron セットアップ

**Files:**
- Create: `setup_cron.sh`

- [ ] **Step 1: setup_cron.sh を作成する**

```bash
#!/bin/bash
# Tech0 Giver Collector の Cron を登録するスクリプト
set -e

PROJECT_DIR="/Users/shunsuke_arimura/Desktop/projects/Tech0/Marketing/Giverコンテンツ"
VENV_PYTHON="${PROJECT_DIR}/.venv/bin/python"
LOG_DIR="${PROJECT_DIR}/logs"

CRON_JOB="0 8 * * * cd \"${PROJECT_DIR}\" && ${VENV_PYTHON} run_collector.py >> ${LOG_DIR}/collector.log 2>&1"

# 既存のエントリを確認して重複登録を避ける
if crontab -l 2>/dev/null | grep -q "run_collector.py"; then
  echo "⚠️  Cron エントリは既に存在します。スキップします。"
else
  (crontab -l 2>/dev/null; echo "${CRON_JOB}") | crontab -
  echo "✅ Cron を登録しました: 毎日 08:00 に実行"
fi

echo "現在の Cron 設定:"
crontab -l
```

- [ ] **Step 2: 実行権限を付与して登録する**

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

Expected:
```
✅ Cron を登録しました: 毎日 08:00 に実行
現在の Cron 設定:
0 8 * * * cd "...Giverコンテンツ" && .../python run_collector.py >> .../collector.log 2>&1
```

- [ ] **Step 3: コミットする**

```bash
git add setup_cron.sh
git commit -m "chore: Cron セットアップスクリプトを追加"
```

---

## Task 9: 統合テスト（エンドツーエンド確認）

- [ ] **Step 1: RSS URLの疎通確認をする**

```bash
source .venv/bin/activate
python3 -c "
from collector.sources import SOURCES
from collector.fetcher import fetch_feed

for src in SOURCES:
    articles = fetch_feed(src['url'])
    status = '✅' if articles else '❌'
    print(f'{status} {src[\"name\"]}: {len(articles)}件')
"
```

Expected: 各ソースで1件以上取得できること。❌の場合は `sources.py` のURLを正しいものに修正する。

- [ ] **Step 2: フルパイプラインを実行する**

```bash
python run_collector.py
```

- [ ] **Step 3: 生成された inbox ファイルを確認する**

```bash
cat inbox/$(date +%Y-%m-%d)-articles.md | head -50
```

Expected: タイトル・URL・ソース名・Tier情報が正しく出力されている。

- [ ] **Step 4: Claude Code で tech0-giver-draft を実行する**

Claude Code 上で `/tech0-giver-draft` を実行し、`drafts/YYYY-MM-DD.md` が生成されることを確認する。

- [ ] **Step 5: 生成されたドラフトを確認する**

```bash
cat drafts/$(date +%Y-%m-%d).md
```

Expected: 3件のLINE文面案がフォーマット通りに出力されている。

- [ ] **Step 6: GitHub PR が作成されていることを確認する**

```bash
gh pr list
```

Expected: `[DRAFT] YYYY-MM-DD Giver LINE コンテンツ案` のPRが表示される。

- [ ] **Step 7: 最終コミット**

```bash
git add -A
git commit -m "chore: 統合テスト完了・プロトタイプ動作確認済み"
```

---

## 実装後チェックリスト

- [ ] 全テストが通っている（`pytest --cov=collector` で 80%以上）
- [ ] 全 Tier 1 ソースから記事が取得できている
- [ ] `/tech0-giver-draft` でLINE文面案が3件生成される
- [ ] GitHub PRが自動作成される
- [ ] Cron が毎朝8時に登録されている
- [ ] `inbox/` が `.gitignore` に含まれている

---

## 将来対応（V2）

- Tier 1.5: X API連携（インフルエンサー投稿収集）
- マルチプラットフォーム出力（X用・note用・PPT用の追加コマンド）
- ABテスト機能（タイトルバリエーション生成）
- KPI計測基盤との連携
