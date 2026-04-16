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
