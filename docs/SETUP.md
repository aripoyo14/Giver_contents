# セットアップ・開発ガイド

## ディレクトリ構成

```
Giver_contents/
├── collector/          # RSS 収集モジュール
│   ├── sources.py      #   フィード定義（Tier 1 / Tier 2）
│   ├── fetcher.py      #   feedparser によるフィード取得
│   ├── processor.py    #   重複除去・日付フィルター・ソート
│   └── writer.py       #   inbox/ への Markdown 出力
├── inbox/              # Collector の出力先（日次記事一覧）
├── drafts/             # LINE ドラフト（Git 追跡対象）
├── logs/               # Cron 実行ログ
├── tests/              # pytest テスト
├── mtg_note/           # 会議メモ
├── docs/               # 設計書・実装計画
├── .claude/commands/   # Claude Code カスタムコマンド
├── run_collector.py    # Cron エントリーポイント
├── setup_cron.sh       # Cron 登録スクリプト
└── requirements.txt    # Python 依存パッケージ
```

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使い方

### 1. 記事を収集する

```bash
python run_collector.py
```

Tier 1（TechCrunch, MIT Technology Review, The Verge, OpenAI Blog, Google DeepMind Blog）と Tier 2（Qiita, Zenn）の RSS フィードから記事を取得し、重複除去・直近14日フィルターを経て `inbox/YYYY-MM-DD-articles.md` に保存する。

### 2. LINE ドラフトを生成する

Claude Code で `/tech0-giver-draft` コマンドを実行する。

`inbox/` の最新記事を 4 軸（学習価値・生活直結度・発見価値・初学者親和性）でスコアリングし、上位 10 件の LINE 文面を `drafts/YYYY-MM-DD.md` に出力する。

### 3. Cron で自動化する（任意）

```bash
bash setup_cron.sh
```

毎朝 8:00 に `run_collector.py` を自動実行する crontab エントリを登録する。

> **注意:** `setup_cron.sh` 内の `PROJECT_DIR` のパスが実際のディレクトリ名（`Giver_contents`）と異なる場合があるため、登録前に確認・修正すること。

## テスト

```bash
pytest tests/ -v
```

## 技術スタック

- Python 3
- feedparser / requests / beautifulsoup4 / python-dateutil
- Claude Code（ドラフト生成）
- GitHub CLI（PR 作成）
