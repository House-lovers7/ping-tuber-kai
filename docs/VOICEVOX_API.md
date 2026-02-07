# VOICEVOX API 仕様

## 概要

VOICEVOX Engineは、テキストから音声を合成するTTSエンジン。
本プロジェクトでは、`audio_query` APIが返すモーラタイミングデータを活用する。

公式API仕様: [VOICEVOX Engine API](https://voicevox.github.io/voicevox_engine/api/)

---

## 使用するエンドポイント

### 1. POST /audio_query

テキストから音声合成用のクエリを生成。

**リクエスト**
```
POST /audio_query?text=こんにちは&speaker=1
```

**レスポンス例**
```json
{
  "accent_phrases": [
    {
      "moras": [
        {
          "text": "コ",
          "consonant": "k",
          "consonant_length": 0.100,
          "vowel": "o",
          "vowel_length": 0.157,
          "pitch": 5.71
        },
        {
          "text": "ン",
          "consonant": null,
          "consonant_length": null,
          "vowel": "N",
          "vowel_length": 0.150,
          "pitch": 5.65
        },
        {
          "text": "ニ",
          "consonant": "n",
          "consonant_length": 0.080,
          "vowel": "i",
          "vowel_length": 0.120,
          "pitch": 5.50
        },
        {
          "text": "チ",
          "consonant": "ch",
          "consonant_length": 0.090,
          "vowel": "i",
          "vowel_length": 0.100,
          "pitch": 5.40
        },
        {
          "text": "ワ",
          "consonant": "w",
          "consonant_length": 0.050,
          "vowel": "a",
          "vowel_length": 0.200,
          "pitch": 5.30
        }
      ],
      "accent": 3,
      "pause_mora": null,
      "is_interrogative": false
    }
  ],
  "speedScale": 1.0,
  "pitchScale": 0.0,
  "intonationScale": 1.0,
  "volumeScale": 1.0,
  "prePhonemeLength": 0.1,
  "postPhonemeLength": 0.1,
  "outputSamplingRate": 24000,
  "outputStereo": false
}
```

### 2. POST /synthesis

audio_queryの結果を使って音声を合成。

**リクエスト**
```
POST /synthesis?speaker=1
Content-Type: application/json

{audio_queryのレスポンス全体}
```

**レスポンス**
- `audio/wav` 形式のバイナリデータ

---

## モーラ（Mora）データ構造

```json
{
  "text": "コ",           // 表示用テキスト（カタカナ）
  "consonant": "k",       // 子音（null の場合あり）
  "consonant_length": 0.100,  // 子音の長さ（秒）
  "vowel": "o",           // 母音
  "vowel_length": 0.157,  // 母音の長さ（秒）
  "pitch": 5.71           // ピッチ（音高）
}
```

### 重要なポイント

1. **モーラの長さ** = `consonant_length` + `vowel_length`
2. **子音がない場合**: `consonant` と `consonant_length` は `null`
3. **無声母音**: 大文字で表記（"A", "I", "U", "E", "O"）
4. **撥音（ん）**: `vowel` = "N"

---

## 母音の種類

### 有声母音（小文字）
| 母音 | IPA | 説明 |
|-----|-----|------|
| a | /a/ | あ |
| i | /i/ | い |
| u | /ɯ/ | う |
| e | /e/ | え |
| o | /o/ | お |
| N | /ɴ/ | ん（撥音） |

### 無声母音（大文字）
| 母音 | 説明 |
|-----|------|
| A | 無声の「あ」 |
| I | 無声の「い」（例: 「し」「ち」の母音部） |
| U | 無声の「う」（例: 「す」「つ」の母音部） |
| E | 無声の「え」 |
| O | 無声の「お」 |

無声母音は口を動かさず発音されるため、`closed.png` を表示する。

---

## 母音→Visemeマッピング

| 母音 | IPA | 口形状 | 画像ファイル |
|-----|-----|--------|-------------|
| a | /a/ | 大きく開く | `a.png` |
| i | /i/ | 横に広げる | `i.png` |
| u | /ɯ/ | すぼめる | `u.png` |
| e | /e/ | 少し開く+横 | `e.png` |
| o | /o/ | 丸く開く | `o.png` |
| N | /ɴ/ | 軽く閉じ | `n.png` |
| A, I, U, E, O | - | 閉じたまま | `closed.png` |
| (子音のみ) | - | 閉じ | `closed.png` |
| (ポーズ) | - | 閉じ | `closed.png` |

---

## pause_mora（ポーズモーラ）

アクセント句の末尾にポーズがある場合:

```json
{
  "accent_phrases": [
    {
      "moras": [...],
      "pause_mora": {
        "text": "、",
        "consonant": null,
        "consonant_length": null,
        "vowel": "pau",
        "vowel_length": 0.300,
        "pitch": 0.0
      }
    }
  ]
}
```

`vowel` = "pau" の場合は `closed.png` を表示。

---

## タイムライン計算例

テキスト: 「こんにちは」

```
時刻    音素    Viseme
─────────────────────────
0.000   (開始)  closed
0.000   k       closed  ← 子音中は閉じ
0.100   o       o.png   ← 母音開始
0.257   N       n.png
0.407   n       closed
0.487   i       i.png
0.607   ch      closed
0.697   i       i.png
0.797   w       closed
0.847   a       a.png
1.047   (終了)  closed
```

### 計算ロジック

```python
current_time = 0.0
timeline = []

for phrase in audio_query["accent_phrases"]:
    for mora in phrase["moras"]:
        # 子音部分
        if mora["consonant_length"]:
            timeline.append({
                "start": current_time,
                "duration": mora["consonant_length"],
                "viseme": "closed"
            })
            current_time += mora["consonant_length"]

        # 母音部分
        vowel = mora["vowel"]
        viseme = get_viseme(vowel)  # マッピング適用
        timeline.append({
            "start": current_time,
            "duration": mora["vowel_length"],
            "viseme": viseme
        })
        current_time += mora["vowel_length"]

    # ポーズモーラ
    if phrase.get("pause_mora"):
        pause = phrase["pause_mora"]
        timeline.append({
            "start": current_time,
            "duration": pause["vowel_length"],
            "viseme": "closed"
        })
        current_time += pause["vowel_length"]
```

---

## 話者ID（speaker）

VOICEVOXには複数の話者が存在する。

### 主な話者
| ID | 名前 |
|----|------|
| 0 | 四国めたん（あまあま） |
| 1 | ずんだもん（あまあま） |
| 2 | 四国めたん（ノーマル） |
| 3 | ずんだもん（ノーマル） |
| ... | ... |

話者一覧は `/speakers` エンドポイントで取得可能。

---

## 参考リンク

- [VOICEVOX Engine API](https://voicevox.github.io/voicevox_engine/api/)
- [VOICEVOX GitHub](https://github.com/VOICEVOX/voicevox_engine)
- [VOICEVOX 公式サイト](https://voicevox.hiroshiba.jp/)
