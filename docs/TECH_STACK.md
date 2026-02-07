# ping-tuber-kai 技術スタック

## Pythonバージョン: 3.13

2024年10月リリース、現在安定版。

### 採用理由
- 新しいインタラクティブREPL（マルチライン編集、カラー対応）
- 実験的フリースレッドモード（将来の並列処理に備える）
- パフォーマンス改善

参考: [Python 3.13 新機能](https://docs.python.org/3/whatsnew/3.13.html)

---

## パッケージマネージャ: uv

Rustで書かれた超高速パッケージマネージャ。

### 採用理由
- pip比 10-100倍速
- `pip`, `virtualenv`, `pip-tools`, `pipx`, `pyenv`を統合
- `uv.lock`による完全な再現性
- プロジェクト管理の簡素化

参考: [uv公式ドキュメント](https://docs.astral.sh/uv/guides/projects/)

---

## GUI選択: PyGame

### 比較検討

| 選択肢 | 用途 | メリット | デメリット |
|--------|------|----------|------------|
| **PyGame** (採用) | スプライト描画 | シンプル、PNG表示に最適、軽量 | ウィジェット機能弱い |
| PySide6 | フルGUI | Qt製、リッチなUI | 重い、ライセンス注意 |
| Textual | ターミナルTUI | 120FPS、モダン、Web対応も可 | 画像表示に不向き |

### 採用理由
- PNGTuberのスプライト切り替えに最適
- SDL2ベースで安定
- 学習コストが低い

---

## 依存ライブラリ

### pyproject.toml

```toml
[project]
name = "ping-tuber-kai"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "httpx>=0.28.0",           # requests後継、async対応
    "pydantic>=2.10.0",        # データバリデーション
    "pydantic-settings>=2.7.0", # 設定管理
    "sounddevice>=0.5.0",      # 低レイテンシ音声再生
    "soundfile>=0.13.0",       # 音声ファイルI/O
    "numpy>=2.0.0",            # 数値計算
    "pygame>=2.6.0",           # スプライト描画
]

[project.optional-dependencies]
obs = [
    "obsws-python>=1.7.0",     # OBS WebSocket連携
]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.9.0",             # Linter & Formatter
]

[project.scripts]
ping-tuber = "ping_tuber_kai.main:main"
```

---

## ライブラリ選定理由

| ライブラリ | 選定理由 |
|-----------|----------|
| **httpx** | `requests`の後継。asyncネイティブ対応、HTTP/2サポート |
| **pydantic v2** | Rust製コア（v1比5-50倍高速）、VOICEVOXレスポンス解析に最適 |
| **pydantic-settings** | 環境変数・設定ファイルからの設定読み込み |
| **sounddevice** | PyAudioより軽量、クロスプラットフォーム、低レイテンシ |
| **soundfile** | libsndfile wrapper、WAV読み書きに最適 |
| **numpy** | 音声データ処理の標準ライブラリ |
| **pygame 2.6** | SDL2ベース、PNGスプライト切替に実績あり |
| **obsws-python** | OBS WebSocket 5.x対応の公式推奨ライブラリ |
| **ruff** | Linter + Formatter統合（Black + isort + Flake8相当を1ツールで） |
| **pytest** | Python標準のテストフレームワーク |

---

## MotionPNGTuberとの比較

**ping-tuber-kaiは大幅に軽量化**

| 項目 | ping-tuber-kai | MotionPNGTuber |
|------|----------------|----------------|
| 依存パッケージ数 | 約6 | 約15+重量級ML |
| PyTorch/MMDetection | 不要 | 必要（顔検出） |
| 音声特徴抽出 | 不要 | 必要 |
| 精度 | 最高（TTS同期） | 高（音声解析） |
| リアルタイム対応 | 可能 | 困難 |

### 軽量化の理由
- VOICEVOXがモーラタイミングを提供するため、音声解析不要
- 顔検出機能を持たない（PNGTuber専用設計）
- 必要最小限の依存関係

---

## 開発ツール

### ruff

Rust製の高速Linter & Formatter。

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# 自動修正
uv run ruff check --fix .
```

### pytest

```bash
# テスト実行
uv run pytest

# カバレッジ付き
uv run pytest --cov=src
```

---

## システム要件

### 必須
- Python 3.13+
- VOICEVOX Engine（ローカル起動）
- macOS / Linux / Windows

### オプション
- OBS Studio + WebSocket プラグイン（OBS連携時）

### VOICEVOX Engine起動

```bash
# Docker使用時
docker run --rm -p 50021:50021 voicevox/voicevox_engine:cpu-latest

# またはローカルインストール版を起動
```

デフォルトポート: `http://localhost:50021`
