"""フレーム単位スケジューラモジュール."""

from dataclasses import dataclass

from ..config import settings
from .phoneme import PhonemeTimeline
from .viseme import Viseme, get_viseme


@dataclass
class MouthFrame:
    """フレーム単位の口形状."""

    frame: int  # フレーム番号
    time: float  # 時刻（秒）
    viseme: Viseme  # 口形状


# 型エイリアス
MouthSchedule = list[MouthFrame]


def create_mouth_schedule(
    timeline: PhonemeTimeline,
    total_duration: float,
    fps: int | None = None,
) -> MouthSchedule:
    """音素タイムラインからMouthScheduleを生成.

    Args:
        timeline: 音素タイムライン
        total_duration: 総再生時間（秒）
        fps: フレームレート（デフォルト: 設定から取得）

    Returns:
        MouthSchedule: フレーム単位の口形状リスト
    """
    frame_rate = fps or settings.fps
    total_frames = int(total_duration * frame_rate) + 1

    schedule: MouthSchedule = []

    for frame in range(total_frames):
        time = frame / frame_rate
        viseme = get_viseme_at_time(timeline, time)
        schedule.append(MouthFrame(frame=frame, time=time, viseme=viseme))

    return schedule


def get_viseme_at_time(timeline: PhonemeTimeline, time: float) -> Viseme:
    """指定時刻のVisemeを取得.

    Args:
        timeline: 音素タイムライン
        time: 時刻（秒）

    Returns:
        Viseme: その時刻の口形状
    """
    for event in timeline:
        if event.start <= time < event.end:
            return get_viseme(event.phoneme, event.is_vowel)

    # タイムライン外は閉じ
    return Viseme.CLOSED


def get_viseme_at_frame(schedule: MouthSchedule, frame: int) -> Viseme:
    """指定フレームのVisemeを取得.

    Args:
        schedule: MouthSchedule
        frame: フレーム番号

    Returns:
        Viseme: そのフレームの口形状
    """
    if 0 <= frame < len(schedule):
        return schedule[frame].viseme
    return Viseme.CLOSED
