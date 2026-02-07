"""音素タイムライン抽出モジュール."""

from dataclasses import dataclass

from ..voicevox.models import AudioQuery


@dataclass
class PhonemeEvent:
    """音素イベント."""

    phoneme: str  # 音素（"a", "i", "u", "e", "o", "N", "k", "pau", etc.）
    start: float  # 開始時刻（秒）
    duration: float  # 持続時間（秒）
    is_vowel: bool  # 母音かどうか
    is_voiced: bool  # 有声音かどうか（大文字母音=無声）

    @property
    def end(self) -> float:
        """終了時刻（秒）."""
        return self.start + self.duration


# 型エイリアス
PhonemeTimeline = list[PhonemeEvent]


def extract_phoneme_timeline(query: AudioQuery) -> PhonemeTimeline:
    """AudioQueryから音素タイムラインを抽出.

    Args:
        query: VOICEVOX AudioQuery

    Returns:
        PhonemeTimeline: 音素イベントのリスト（時系列順）
    """
    timeline: PhonemeTimeline = []
    current_time = query.pre_phoneme_length  # 開始無音を考慮

    for phrase in query.accent_phrases:
        for mora in phrase.moras:
            # 子音部分
            if mora.consonant and mora.consonant_length:
                timeline.append(
                    PhonemeEvent(
                        phoneme=mora.consonant,
                        start=current_time,
                        duration=mora.consonant_length,
                        is_vowel=False,
                        is_voiced=True,  # 子音は基本的に有声扱い
                    )
                )
                current_time += mora.consonant_length

            # 母音部分
            timeline.append(
                PhonemeEvent(
                    phoneme=mora.vowel,
                    start=current_time,
                    duration=mora.vowel_length,
                    is_vowel=True,
                    is_voiced=mora.is_voiced_vowel,
                )
            )
            current_time += mora.vowel_length

        # ポーズモーラ
        if phrase.pause_mora:
            pause = phrase.pause_mora
            timeline.append(
                PhonemeEvent(
                    phoneme="pau",
                    start=current_time,
                    duration=pause.vowel_length,
                    is_vowel=False,
                    is_voiced=False,
                )
            )
            current_time += pause.vowel_length

    return timeline


def get_total_duration(query: AudioQuery) -> float:
    """AudioQueryの総再生時間を計算.

    Args:
        query: VOICEVOX AudioQuery

    Returns:
        float: 総再生時間（秒）
    """
    duration = query.pre_phoneme_length + query.post_phoneme_length

    for phrase in query.accent_phrases:
        for mora in phrase.moras:
            duration += mora.total_length
        if phrase.pause_mora:
            duration += phrase.pause_mora.vowel_length

    return duration
