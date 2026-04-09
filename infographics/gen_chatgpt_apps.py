"""
Infographic generator: ChatGPT × 日常アプリ連携
Output: infographics/2026-04-09-chatgpt-apps.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
import matplotlib.font_manager as fm

# ── フォント設定 ──────────────────────────────────────────────────────────
jp_fonts = [f.name for f in fm.fontManager.ttflist if f.name == "Hiragino Sans"]
jp_font = jp_fonts[0] if jp_fonts else "DejaVu Sans"
plt.rcParams["font.family"] = jp_font

# ── キャンバス ────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10.8, 13.0), dpi=100)
fig.patch.set_facecolor("#0f0f1a")
ax.set_facecolor("#0f0f1a")
ax.set_xlim(0, 10.8)
ax.set_ylim(0, 13.0)
ax.axis("off")

# ── ヘッダー帯 ────────────────────────────────────────────────────────────
header = FancyBboxPatch((0, 11.5), 10.8, 1.5,
                        boxstyle="square,pad=0", linewidth=0,
                        facecolor="#10a37f")
ax.add_patch(header)

ax.text(5.4, 12.25, "今日のテック / AIニュース",
        ha="center", va="center",
        fontsize=20, fontweight="bold", color="white")

ax.text(5.4, 11.75, "Tech0 Giver",
        ha="center", va="center",
        fontsize=13, color="#c0f0e0")

# ── タイトルブロック ──────────────────────────────────────────────────────
ax.text(5.4, 11.0, "ChatGPT  x  日常アプリが合体",
        ha="center", va="center",
        fontsize=28, fontweight="bold", color="#ffffff")

ax.text(5.4, 10.45, "会話するだけで  注文 / 手配 / 再生  が完結",
        ha="center", va="center",
        fontsize=15, color="#8080a0")

ax.axhline(y=10.1, xmin=0.05, xmax=0.95, color="#2a2a4a", linewidth=1.2)

# ── アプリタイル ──────────────────────────────────────────────────────────
apps = [
    {"name": "Uber",      "label": "移動手配",  "abbr": "Ur",  "color": "#f5c518"},
    {"name": "Spotify",   "label": "音楽再生",  "abbr": "Sp",  "color": "#1db954"},
    {"name": "DoorDash",  "label": "食事注文",  "abbr": "DD",  "color": "#ff3008"},
    {"name": "Kayak",     "label": "旅行計画",  "abbr": "Kk",  "color": "#ff690f"},
    {"name": "OpenTable", "label": "レストラン", "abbr": "OT", "color": "#da3743"},
    {"name": "Instacart", "label": "食材注文",  "abbr": "IC",  "color": "#43b02a"},
]

tile_w, tile_h = 2.9, 2.7
gap_x, gap_y = 0.3, 0.35
cols = 3
total_w = cols * tile_w + (cols - 1) * gap_x
start_x = (10.8 - total_w) / 2
start_y = 9.5

for i, app in enumerate(apps):
    col = i % cols
    row = i // cols
    x = start_x + col * (tile_w + gap_x)
    y = start_y - row * (tile_h + gap_y)

    # タイル背景
    tile = FancyBboxPatch((x, y - tile_h), tile_w, tile_h,
                          boxstyle="round,pad=0.12", linewidth=2,
                          edgecolor=app["color"], facecolor="#15151f")
    ax.add_patch(tile)

    # カラーバッジ（円）
    cx, cy = x + tile_w / 2, y - tile_h / 2 + 0.6
    badge = Circle((cx, cy), 0.52, color=app["color"], zorder=3)
    ax.add_patch(badge)

    # 略称テキスト（バッジ内）
    ax.text(cx, cy, app["abbr"],
            ha="center", va="center",
            fontsize=15, fontweight="bold", color="white", zorder=4)

    # アプリ名
    ax.text(x + tile_w / 2, y - tile_h / 2 - 0.28,
            app["name"],
            ha="center", va="center",
            fontsize=15, fontweight="bold", color="#ffffff")

    # ラベル（用途）
    ax.text(x + tile_w / 2, y - tile_h / 2 - 0.72,
            app["label"],
            ha="center", va="center",
            fontsize=12, color="#8090a0")

# ── ChatGPT 中心説明 ──────────────────────────────────────────────────────
center_y = start_y - 1 * (tile_h + gap_y) - tile_h - 0.5
ax.text(5.4, center_y,
        "これらすべてをChatGPTの会話から操作できる",
        ha="center", va="center",
        fontsize=14, color="#a0b0c0")

# ── 試し方ボックス ────────────────────────────────────────────────────────
box_y = center_y - 0.6
how_bg = FancyBboxPatch((0.6, box_y - 1.4), 9.6, 1.6,
                         boxstyle="round,pad=0.2", linewidth=1.5,
                         edgecolor="#10a37f", facecolor="#0c1f1a")
ax.add_patch(how_bg)

ax.text(5.4, box_y - 0.35, "試し方",
        ha="center", va="center",
        fontsize=14, fontweight="bold", color="#10a37f")

ax.text(5.4, box_y - 0.82,
        "ChatGPTアプリ  ->  左上メニュー  ->  接続済みアプリ",
        ha="center", va="center",
        fontsize=13, color="#c0f0e0")

ax.text(5.4, box_y - 1.2,
        "無料プランでも一部利用可",
        ha="center", va="center",
        fontsize=11, color="#506060")

# ── フッター ──────────────────────────────────────────────────────────────
ax.text(5.4, 0.3, "Source: TechCrunch 2026.04.06",
        ha="center", va="center",
        fontsize=9, color="#303050")

# ── 出力 ──────────────────────────────────────────────────────────────────
out_path = "infographics/2026-04-09-chatgpt-apps.png"
plt.tight_layout(pad=0)
plt.savefig(out_path, dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {out_path}")
