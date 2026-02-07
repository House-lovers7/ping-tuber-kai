# ping-tuber-kai

VOICEVOX母音リップシンクを活用したPNGTuberアプリケーション。

## プロジェクト概要

- **目的**: VOICEVOXのモーラタイミングデータを活用した高精度リップシンク
- **技術スタック**: Python 3.13, uv, PyGame, httpx, Pydantic
- **アーキテクチャ**: `docs/ARCHITECTURE.md` 参照

## ディレクトリ構成

```
src/ping_tuber_kai/
├── voicevox/     # VOICEVOX APIクライアント
├── lipsync/      # 音素タイムライン・Viseme変換
├── player/       # 音声再生・同期エンジン
├── output/       # PyGame表示・OBS連携
└── ui/           # 統合GUIアプリ
```

## 開発コマンド

```bash
# 依存インストール
uv sync --extra dev

# テスト実行
uv run pytest -v

# Lint
uv run ruff check .

# Format
uv run ruff format .

# プレースホルダー画像生成
uv run python scripts/generate_placeholder_images.py

# アプリ実行（VOICEVOX Engine起動必須）
uv run ping-tuber --text "こんにちは"
```

## VOICEVOX Engine

```bash
# Docker起動
docker run --rm -p 50021:50021 voicevox/voicevox_engine:cpu-latest
```

## 重要なファイル

- `src/ping_tuber_kai/lipsync/viseme.py` - 母音→口形状マッピング
- `src/ping_tuber_kai/voicevox/models.py` - APIレスポンスモデル
- `src/ping_tuber_kai/player/sync.py` - 同期再生エンジン

## コーディング規約

- Linter/Formatter: ruff
- 行長: 100文字
- Python: 3.13+
- 型ヒント必須
