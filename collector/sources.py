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
