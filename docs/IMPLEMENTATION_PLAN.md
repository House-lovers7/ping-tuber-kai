# ping-tuber-kai 実装計画

## 実装ステップ

### Phase 1: 基盤構築

1. **uvプロジェクト初期化**
   - `uv init` でプロジェクト作成
   - `pyproject.toml` に依存関係定義

2. **VOICEVOX APIクライアント実装**
   - `audio_query` エンドポイント呼び出し
   - `synthesis` エンドポイント呼び出し
   - エラーハンドリング

3. **Pydanticモデル定義**
   - `AudioQuery`: クエリ全体
   - `AccentPhrase`: アクセント句
   - `Mora`: モーラ（音素単位）

---

### Phase 2: 音素タイムライン

1. **audio_queryレスポンスからモーラタイミング抽出**
   - `accent_phrases` → `moras` を走査
   - 各モーラの `consonant_length` + `vowel_length` を取得

2. **PhonemeTimeline型定義**
   ```python
   @dataclass
   class PhonemeEvent:
       phoneme: str      # 音素（"a", "i", "u", "e", "o", "N", etc.）
       start: float      # 開始時刻（秒）
       duration: float   # 持続時間（秒）
       is_voiced: bool   # 有声音かどうか（大文字母音=無声）

   PhonemeTimeline = list[PhonemeEvent]
   ```

3. **累積時間計算ロジック**
   - モーラを順に走査し、開始時刻を累積計算
   - `pauseMora` の処理も含める

---

### Phase 3: Viseme変換

1. **母音→口形状マッピング辞書**
   ```python
   VOWEL_TO_VISEME = {
       "a": "a",      # 大きく開く
       "i": "i",      # 横に広げる
       "u": "u",      # すぼめる
       "e": "e",      # 少し開く+横
       "o": "o",      # 丸く開く
       "N": "n",      # 軽く閉じ
       # 大文字（無声母音）→ closed
       "A": "closed",
       "I": "closed",
       "U": "closed",
       "E": "closed",
       "O": "closed",
   }
   ```

2. **フレームレート変換**
   - 秒 → フレーム番号への変換
   - デフォルト: 60 FPS

3. **MouthSchedule生成**
   ```python
   @dataclass
   class MouthFrame:
       frame: int
       viseme: str  # "a", "i", "u", "e", "o", "n", "closed"

   MouthSchedule = list[MouthFrame]
   ```

---

### Phase 4: 同期再生

1. **sounddeviceで音声再生**
   - WAVデータをnumpy配列として読み込み
   - 非ブロッキング再生
   - 再生開始時刻の記録

2. **経過時間に基づく口形状選択**
   - 現在時刻からフレーム番号を計算
   - MouthScheduleから該当Visemeを取得

3. **PyGameでPNG表示**
   - 口形状画像のプリロード
   - フレームごとの画像切替
   - 60 FPSメインループ

---

### Phase 5: 統合・調整

1. **GUI統合**
   - テキスト入力フィールド
   - 話者選択（VOICEVOX speaker_id）
   - 再生ボタン

2. **OBS WebSocket連携実装（オプション）**
   - obsws-pythonによる接続
   - ソース表示/非表示の切替
   - シーンアイテムの操作

3. **口形状切替のスムージング（オプション）**
   - 急激な切替を緩和
   - 中間フレームの補間

---

## 実行コマンド

```bash
# プロジェクト初期化
uv init ping-tuber-kai
cd ping-tuber-kai

# 依存インストール
uv sync

# OBS連携も使う場合
uv sync --extra obs

# 実行
uv run ping-tuber --text "こんにちは"
uv run ping-tuber --text "こんにちは" --obs  # OBS連携有効
```

---

## 検証方法

### 1. 単体テスト

各モジュールのユニットテスト:
- `test_voicevox.py`: APIクライアントのモック検証
- `test_lipsync.py`: 音素抽出・Viseme変換のロジック検証
- `test_player.py`: 同期エンジンのタイミング検証

### 2. 統合テスト

1. テキスト「こんにちは」を入力
2. VOICEVOX APIからaudio_query取得
3. 音素タイムラインが正しく抽出されることを確認
4. 音声再生と口形状切替が同期することを目視確認

期待される音素タイムライン（例）:
```
k → o → N → n → i → ch → i → w → a
```

### 3. エンドツーエンドテスト

- GUIでテキスト入力 → 発話 → 口パク表示
- 遅延・ズレがないことを目視確認
- 各母音で正しい口形状が表示されることを確認

---

## マイルストーン

| Phase | 完了条件 |
|-------|---------|
| Phase 1 | VOICEVOX APIからaudio_query取得成功 |
| Phase 2 | PhonemeTimelineが正しく生成される |
| Phase 3 | MouthScheduleが正しく生成される |
| Phase 4 | 音声と口形状が同期して再生される |
| Phase 5 | GUIから一連の操作が可能 |
