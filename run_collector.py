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
