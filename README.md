# ping-tuber-kai

[![CI](https://github.com/House-lovers7/ping-tuber-kai/actions/workflows/ci.yml/badge.svg)](https://github.com/House-lovers7/ping-tuber-kai/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

VOICEVOX APIの **mora（モーラ）タイミングデータ**を活用した、AIUEO母音ベースの高精度リップシンクPNGTuber。

<!-- デモGIF用プレースホルダー -->
<!-- ![Demo](docs/images/demo.gif) -->

---

## Why I Built This / なぜ作ったか

既存のリップシンクツールは**音声波形解析**に依存しており、以下の課題がありました：

- 重量級の機械学習ライブラリ（PyTorch等）が必要
- 音声解析による遅延・精度の限界
- リアルタイム処理が困難

**ping-tuber-kai** は発想を転換し、**TTSエンジン（VOICEVOX）が内部で持つ音素タイミングデータ**を直接活用することで、これらの課題を解決しました。

### Technical Insight / 技術的なポイント

VOICEVOXの `audio_query` APIは、音声合成前に各モーラ（音素単位）の正確なタイミングを返します：

```json
{
  "moras": [{
    "text": "コ",
    "consonant": "k",
    "consonant_length": 0.100,
    "vowel": "o",
    "vowel_length": 0.157
  }]
}
```

このデータを活用することで、**音声生成と完全同期したリップシンク**を実現しています。

---

## Features / 特徴

| 特徴 | 説明 |
|------|------|
| **最高精度** | TTSエンジンと完全同期（±0ms） |
| **軽量** | PyTorch/MFA等の重量級依存なし |
| **シンプル** | VOICEVOX Engineのみで動作 |
| **OBS連携** | WebSocket経由でソース切替可能 |
| **モダン技術** | Python 3.13, uv, Pydantic v2 |

---

## Tech Stack / 技術スタック

| カテゴリ | 技術 |
|---------|------|
| Language | Python 3.13 |
| Package Manager | uv (Rust製、pip比10-100倍高速) |
| HTTP Client | httpx (async対応) |
| Validation | Pydantic v2 (Rust製コア) |
| Audio | sounddevice + soundfile |
| Display | PyGame 2.6 (SDL2) |
| Linter/Formatter | ruff |
| CI/CD | GitHub Actions |

---

## Architecture / アーキテクチャ

```
テキスト入力
    ↓
VOICEVOX audio_query API
    ↓
┌──────────────┬──────────────┐
│ synthesis    │ mora timing  │
│ (WAV生成)    │ (タイミング)  │
└──────────────┴──────────────┘
    ↓                ↓
    └────┬───────────┘
         ↓
    同期再生エンジン
         ↓
┌────────┬────────┬────────┐
│ 音声   │ PyGame │ OBS    │
│ 再生   │ 表示   │ 連携   │
└────────┴────────┴────────┘
```

### Module Structure / モジュール構成

```
src/ping_tuber_kai/
├── voicevox/      # VOICEVOX APIクライアント
│   ├── client.py  # HTTP通信、エラーハンドリング
│   └── models.py  # Pydanticモデル（AudioQuery, Mora等）
├── lipsync/       # リップシンクエンジン
│   ├── phoneme.py # 音素タイムライン抽出
│   ├── viseme.py  # 母音→口形状マッピング
│   └── scheduler.py # フレームスケジューラ
├── player/        # 再生エンジン
│   ├── audio.py   # 低レイテンシ音声再生
│   └── sync.py    # 音声・映像同期制御
└── output/        # 出力
    ├── pygame_window.py  # PyGame表示
    └── obs_websocket.py  # OBS連携
```

---

## Requirements / 必要要件

- Python 3.13+
- VOICEVOX Engine（ローカル起動）
- uv（パッケージマネージャ）

## Installation / インストール

```bash
# リポジトリをクローン
git clone https://github.com/House-lovers7/ping-tuber-kai.git
cd ping-tuber-kai

# 依存インストール
uv sync

# OBS連携も使う場合
uv sync --extra obs

# 開発用ツールも含める場合
uv sync --extra dev
```

## VOICEVOX Engineの起動

```bash
# Dockerの場合
docker run --rm -p 50021:50021 voicevox/voicevox_engine:cpu-latest

# またはローカルインストール版を起動
```

---

## Usage / 使い方

### 基本的な使い方

```bash
# テキストを発話
uv run ping-tuber --text "こんにちは"

# 話者を指定（デフォルト: 1 = ずんだもん）
uv run ping-tuber --text "こんにちは" --speaker 3
```

### 話者一覧の確認

```bash
uv run ping-tuber --list-speakers
```

### VOICEVOX接続確認

```bash
uv run ping-tuber --check
```

### OBS連携

```bash
# OBS WebSocket連携を有効化
uv run ping-tuber --text "こんにちは" --obs
```

OBS側で以下のソースを作成してください：
- `mouth_a` - あ（大きく開く）
- `mouth_i` - い（横に広げる）
- `mouth_u` - う（すぼめる）
- `mouth_e` - え（少し開く+横）
- `mouth_o` - お（丸く開く）
- `mouth_n` - ん（軽く閉じ）
- `mouth_closed` - 閉じ

### カスタムアセット

```bash
uv run ping-tuber --text "こんにちは" --assets ./my_assets/mouth
```

---

## Environment Variables / 環境変数

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `PING_TUBER_VOICEVOX_HOST` | `http://localhost:50021` | VOICEVOX Engine URL |
| `PING_TUBER_VOICEVOX_SPEAKER_ID` | `1` | 話者ID |
| `PING_TUBER_WINDOW_WIDTH` | `400` | ウィンドウ幅 |
| `PING_TUBER_WINDOW_HEIGHT` | `400` | ウィンドウ高さ |
| `PING_TUBER_FPS` | `60` | フレームレート |
| `PING_TUBER_OBS_HOST` | `localhost` | OBS WebSocketホスト |
| `PING_TUBER_OBS_PORT` | `4455` | OBS WebSocketポート |
| `PING_TUBER_OBS_PASSWORD` | (空) | OBS WebSocketパスワード |

---

## Development / 開発

### テスト実行

```bash
uv run pytest -v
```

### Lint & Format

```bash
uv run ruff check .
uv run ruff format .
```

### プレースホルダー画像生成

```bash
uv run python scripts/generate_placeholder_images.py
```

---

## Documentation / ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | アーキテクチャ設計 |
| [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | 実装計画 |
| [TECH_STACK.md](docs/TECH_STACK.md) | 技術スタック選定理由 |
| [VOICEVOX_API.md](docs/VOICEVOX_API.md) | VOICEVOX API仕様 |

---

## License / ライセンス

MIT License - see [LICENSE](LICENSE)

## References / 参考

- [VOICEVOX Engine API](https://voicevox.github.io/voicevox_engine/api/)
- [MotionPNGTuber](https://github.com/rotejin/MotionPNGTuber)
