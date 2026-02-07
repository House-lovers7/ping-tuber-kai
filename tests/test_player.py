"""プレイヤーモジュールのテスト."""


from ping_tuber_kai.lipsync.phoneme import PhonemeEvent
from ping_tuber_kai.lipsync.scheduler import create_mouth_schedule
from ping_tuber_kai.lipsync.viseme import Viseme
from ping_tuber_kai.player.audio import PlaybackState


class TestPlaybackState:
    """PlaybackStateのテスト."""

    def test_initial_state(self):
        """初期状態."""
        state = PlaybackState()
        assert state.is_playing is False
        assert state.elapsed_time == 0.0
        assert state.is_finished is True

    def test_elapsed_time_when_not_playing(self):
        """非再生時の経過時間は0."""
        state = PlaybackState()
        state.is_playing = False
        assert state.elapsed_time == 0.0


class TestMouthScheduleIntegration:
    """MouthSchedule統合テスト."""

    def test_schedule_for_konnichiwa(self):
        """「こんにちは」のスケジュール."""
        # 簡略化したタイムライン
        timeline = [
            PhonemeEvent(phoneme="k", start=0.0, duration=0.1, is_vowel=False, is_voiced=True),
            PhonemeEvent(phoneme="o", start=0.1, duration=0.15, is_vowel=True, is_voiced=True),
            PhonemeEvent(phoneme="N", start=0.25, duration=0.15, is_vowel=True, is_voiced=True),
            PhonemeEvent(phoneme="n", start=0.4, duration=0.08, is_vowel=False, is_voiced=True),
            PhonemeEvent(phoneme="i", start=0.48, duration=0.12, is_vowel=True, is_voiced=True),
            PhonemeEvent(phoneme="ch", start=0.6, duration=0.09, is_vowel=False, is_voiced=True),
            PhonemeEvent(phoneme="i", start=0.69, duration=0.1, is_vowel=True, is_voiced=True),
            PhonemeEvent(phoneme="w", start=0.79, duration=0.05, is_vowel=False, is_voiced=True),
            PhonemeEvent(phoneme="a", start=0.84, duration=0.2, is_vowel=True, is_voiced=True),
        ]

        schedule = create_mouth_schedule(timeline, total_duration=1.04, fps=30)

        # 特定フレームでの口形状確認
        # 0.1秒 = フレーム3: o
        assert schedule[3].viseme == Viseme.O

        # 0.3秒 = フレーム9: N
        assert schedule[9].viseme == Viseme.N

        # 0.5秒 = フレーム15: i
        assert schedule[15].viseme == Viseme.I

        # 0.9秒 = フレーム27: a
        assert schedule[27].viseme == Viseme.A

    def test_unvoiced_vowel_is_closed(self):
        """無声母音は閉じ."""
        timeline = [
            PhonemeEvent(
                phoneme="s", start=0.0, duration=0.1, is_vowel=False, is_voiced=True
            ),
            PhonemeEvent(
                phoneme="U", start=0.1, duration=0.1, is_vowel=True, is_voiced=False
            ),  # 無声
        ]

        schedule = create_mouth_schedule(timeline, total_duration=0.2, fps=10)

        # 無声母音部分は閉じ
        assert schedule[1].viseme == Viseme.CLOSED
