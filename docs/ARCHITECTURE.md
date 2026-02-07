# ping-tuber-kai アーキテクチャ設計

## 概要

VOICEVOX APIの `audio_query` から取得できる **mora（モーラ）タイミングデータ**を活用し、AIUEO母音ベースの高精度リップシンクを実現する。

## Route A（TTS内部duration）を選択する理由

| 比較項目 | Route A (VOICEVOX) | Route B (MFA) |
|---------|-------------------|---------------|
| 精度 | **最高**（TTS生成と完全同期） | 高（±11-17ms） |
| 追加処理 | **なし** | MFA実行が必要 |
| 実装コスト | **低** | 中〜高 |
| リアルタイム | **対応可** | 困難 |
| 依存関係 | VOICEVOXのみ | MFA + Kaldi |

**結論: Route A一択**

VOICEVOXの `audio_query` APIは既に完全なモーラタイミングを返すため、追加ツール不要。

---

## 設計方針

- **出力形式**: PyGameウィンドウ + OBS WebSocket連携（両方対応）
- **入力ソース**: TTSのみ（VOICEVOX音素データ活用、最高精度）

---

## データフロー図

```
┌─────────────────────────────────────────────────────────────────┐
│                         ping-tuber-kai                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [1] テキスト入力                                                │
│         │                                                       │
│         ▼                                                       │
│  [2] VOICEVOX audio_query API ──────────┐                       │
│         │                               │                       │
│         ▼                               ▼                       │
│  [3] synthesis API              [4] mora timing 抽出            │
│         │                               │                       │
│         ▼                               ▼                       │
│  [5] WAV音声データ              [6] PhonemeTimeline             │
│         │                               │                       │
│         └────────────┬──────────────────┘                       │
│                      ▼                                          │
│              [7] 同期再生エンジン                                │
│                      │                                          │
│         ┌────────────┼────────────┐                             │
│         ▼            ▼            ▼                             │
│    音声出力   PyGame表示     OBS WebSocket                      │
│  (sounddevice)   (メイン)     (オプション)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## プロジェクト構成

```
ping-tuber-kai/
├── pyproject.toml              # uv用設定
├── README.md
├── src/
│   └── ping_tuber_kai/
│       ├── __init__.py
│       ├── main.py             # CLIエントリーポイント
│       ├── config.py           # 設定管理（Pydantic Settings）
│       ├── voicevox/
│       │   ├── __init__.py
│       │   ├── client.py       # VOICEVOX API クライアント
│       │   └── models.py       # Pydantic モデル定義
│       ├── lipsync/
│       │   ├── __init__.py
│       │   ├── phoneme.py      # 音素タイムライン抽出
│       │   ├── viseme.py       # 母音→口形状マッピング
│       │   └── scheduler.py    # フレーム単位スケジューラ
│       ├── player/
│       │   ├── __init__.py
│       │   ├── audio.py        # 音声再生（sounddevice）
│       │   └── sync.py         # 音声・口形状同期エンジン
│       ├── output/
│       │   ├── __init__.py
│       │   ├── pygame_window.py  # PyGame表示（メイン）
│       │   └── obs_websocket.py  # OBS連携（オプション）
│       └── ui/
│           ├── __init__.py
│           └── app.py          # 統合GUIアプリ
├── assets/
│   └── mouth/                  # 口形状PNG素材（7種）
│       ├── a.png               # あ（大きく開く）
│       ├── i.png               # い（横に広げる）
│       ├── u.png               # う（すぼめる）
│       ├── e.png               # え（少し開く+横）
│       ├── o.png               # お（丸く開く）
│       ├── n.png               # ん（軽く閉じ）
│       └── closed.png          # 閉じ
├── docs/
│   ├── ARCHITECTURE.md         # 本ドキュメント
│   ├── IMPLEMENTATION_PLAN.md  # 実装計画
│   ├── TECH_STACK.md           # 技術スタック
│   └── VOICEVOX_API.md         # VOICEVOX API仕様
└── tests/
    ├── test_voicevox.py
    ├── test_lipsync.py
    └── test_player.py
```

---

## モジュール責務

### voicevox/
- `client.py`: VOICEVOX Engine APIとのHTTP通信（httpx使用）
- `models.py`: APIレスポンスのPydanticモデル定義

### lipsync/
- `phoneme.py`: audio_queryからPhonemeTimeline抽出
- `viseme.py`: 母音→口形状（Viseme）マッピング
- `scheduler.py`: フレームレートに基づくスケジューリング

### player/
- `audio.py`: sounddeviceによる低レイテンシ音声再生
- `sync.py`: 音声再生と口形状更新の同期制御

### output/
- `pygame_window.py`: PyGameウィンドウでのPNG表示
- `obs_websocket.py`: OBS WebSocket経由でのソース切替

### ui/
- `app.py`: テキスト入力→発話→表示の統合GUI

---

## 参考資料

- [VOICEVOX Engine API](https://voicevox.github.io/voicevox_engine/api/)
- [MotionPNGTuber GitHub](https://github.com/rotejin/MotionPNGTuber)
