# ping-tuber-kai

VOICEVOX APIの **mora（モーラ）タイミングデータ**を活用した、AIUEO母音ベースの高精度リップシンクPNGTuber。

## 特徴

- **最高精度のリップシンク**: VOICEVOXのTTS生成と完全同期
- **軽量**: PyTorch/MFA等の重量級依存なし
- **シンプル**: VOICEVOX Engineのみで動作
- **OBS連携対応**: OBS WebSocket経由でソース切替可能

## 必要要件

- Python 3.13+
- VOICEVOX Engine（ローカル起動）
- uv（パッケージマネージャ）

## インストール

```bash
# リポジトリをクローン
git clone <repository-url>
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

## 使い方

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

`assets/mouth/` ディレクトリに以下の画像を配置：
- `a.png` - あ
- `i.png` - い
- `u.png` - う
- `e.png` - え
- `o.png` - お
- `n.png` - ん
- `closed.png` - 閉じ

## 環境変数

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

## 開発

### テスト実行

```bash
uv run pytest
```

### Lint & Format

```bash
uv run ruff check .
uv run ruff format .
```

## アーキテクチャ

詳細は [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) を参照。

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

## ドキュメント

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - アーキテクチャ設計
- [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) - 実装計画
- [TECH_STACK.md](docs/TECH_STACK.md) - 技術スタック
- [VOICEVOX_API.md](docs/VOICEVOX_API.md) - VOICEVOX API仕様

## ライセンス

MIT License

## 参考

- [VOICEVOX Engine API](https://voicevox.github.io/voicevox_engine/api/)
- [MotionPNGTuber](https://github.com/rotejin/MotionPNGTuber)
