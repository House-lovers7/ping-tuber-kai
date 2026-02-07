"""リップシンクモジュールのテスト."""

import pytest

from ping_tuber_kai.lipsync.phoneme import (
    PhonemeEvent,
    extract_phoneme_timeline,
    get_total_duration,
)
from ping_tuber_kai.lipsync.scheduler import (
    create_mouth_schedule,
    get_viseme_at_time,
)
from ping_tuber_kai.lipsync.viseme import Viseme, get_viseme
from ping_tuber_kai.voicevox.models import AccentPhrase, AudioQuery, Mora


class TestViseme:
    """Visemeマッピングのテスト."""

    @pytest.mark.parametrize(
        "phoneme,expected",
        [
            ("a", Viseme.A),
            ("i", Viseme.I),
            ("u", Viseme.U),
            ("e", Viseme.E),
            ("o", Viseme.O),
            ("N", Viseme.N),
        ],
    )
    def test_voiced_vowels(self, phoneme: str, expected: Viseme):
        """有声母音のマッピング."""
        assert get_viseme(phoneme, is_vowel=True) == expected

    @pytest.mark.parametrize("phoneme", ["A", "I", "U", "E", "O"])
    def test_unvoiced_vowels(self, phoneme: str):
        """無声母音は閉じ."""
        assert get_viseme(phoneme, is_vowel=True) == Viseme.CLOSED

    def test_consonant(self):
        """子音は閉じ."""
        assert get_viseme("k", is_vowel=False) == Viseme.CLOSED

    def test_pause(self):
        """ポーズは閉じ."""
        assert get_viseme("pau", is_vowel=True) == Viseme.CLOSED


class TestPhonemeTimeline:
    """音素タイムライン抽出のテスト."""

    @pytest.fixture
    def sample_query(self) -> AudioQuery:
        """サンプルAudioQuery（「こんにちは」相当）."""
        moras = [
            Mora(
                text="コ", consonant="k", consonant_length=0.1,
                vowel="o", vowel_length=0.15, pitch=5.0
            ),
            Mora(
                text="ン", consonant=None, consonant_length=None,
                vowel="N", vowel_length=0.15, pitch=5.0
            ),
            Mora(
                text="ニ", consonant="n", consonant_length=0.08,
                vowel="i", vowel_length=0.12, pitch=5.0
            ),
            Mora(
                text="チ", consonant="ch", consonant_length=0.09,
                vowel="i", vowel_length=0.1, pitch=5.0
            ),
            Mora(
                text="ワ", consonant="w", consonant_length=0.05,
                vowel="a", vowel_length=0.2, pitch=5.0
            ),
        ]
        phrase = AccentPhrase(moras=moras, accent=3)
        return AudioQuery(
            accent_phrases=[phrase],
            pre_phoneme_length=0.1,
            post_phoneme_length=0.1,
        )

    def test_extract_timeline(self, sample_query: AudioQuery):
        """タイムライン抽出."""
        timeline = extract_phoneme_timeline(sample_query)

        # 子音5 + 母音5 = 10イベント
        assert len(timeline) == 9  # k, o, N, n, i, ch, i, w, a

        # 最初のイベントはpre_phoneme_length後に開始
        assert timeline[0].start == pytest.approx(0.1)
        assert timeline[0].phoneme == "k"

    def test_timeline_continuity(self, sample_query: AudioQuery):
        """タイムラインの連続性."""
        timeline = extract_phoneme_timeline(sample_query)

        for i in range(len(timeline) - 1):
            # 次のイベントは前のイベントの終了時刻から開始
            assert timeline[i].end == pytest.approx(timeline[i + 1].start)

    def test_get_total_duration(self, sample_query: AudioQuery):
        """総再生時間計算."""
        duration = get_total_duration(sample_query)

        # pre(0.1) + moras + post(0.1)
        expected = 0.1 + (0.1 + 0.15) + 0.15 + (0.08 + 0.12) + (0.09 + 0.1) + (0.05 + 0.2) + 0.1
        assert duration == pytest.approx(expected)


class TestMouthSchedule:
    """MouthScheduleのテスト."""

    def test_create_schedule(self):
        """スケジュール生成."""
        timeline = [
            PhonemeEvent(phoneme="a", start=0.0, duration=0.5, is_vowel=True, is_voiced=True),
            PhonemeEvent(phoneme="i", start=0.5, duration=0.5, is_vowel=True, is_voiced=True),
        ]

        schedule = create_mouth_schedule(timeline, total_duration=1.0, fps=10)

        # 1秒 * 10fps + 1 = 11フレーム
        assert len(schedule) == 11

        # フレーム0-4: a
        for i in range(5):
            assert schedule[i].viseme == Viseme.A

        # フレーム5-9: i
        for i in range(5, 10):
            assert schedule[i].viseme == Viseme.I

    def test_get_viseme_at_time(self):
        """時刻からViseme取得."""
        timeline = [
            PhonemeEvent(phoneme="a", start=0.0, duration=0.5, is_vowel=True, is_voiced=True),
            PhonemeEvent(phoneme="i", start=0.5, duration=0.5, is_vowel=True, is_voiced=True),
        ]

        assert get_viseme_at_time(timeline, 0.25) == Viseme.A
        assert get_viseme_at_time(timeline, 0.75) == Viseme.I
        assert get_viseme_at_time(timeline, 1.5) == Viseme.CLOSED  # 範囲外
