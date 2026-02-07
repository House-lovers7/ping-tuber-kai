"""音声・口形状同期エンジン."""

from collections.abc import Callable
from dataclasses import dataclass

from ..lipsync.phoneme import PhonemeTimeline, extract_phoneme_timeline, get_total_duration
from ..lipsync.scheduler import MouthSchedule, create_mouth_schedule, get_viseme_at_time
from ..lipsync.viseme import Viseme
from ..voicevox.models import AudioQuery
from .audio import AudioPlayer


@dataclass
class SyncData:
    """同期再生用データ."""

    audio_query: AudioQuery
    audio_data: bytes
    timeline: PhonemeTimeline
    schedule: MouthSchedule
    duration: float


class SyncEngine:
    """音声・口形状同期エンジン."""

    def __init__(self, fps: int = 60):
        """初期化.

        Args:
            fps: フレームレート
        """
        self.fps = fps
        self.player = AudioPlayer()
        self._sync_data: SyncData | None = None
        self._viseme_callback: Callable[[Viseme], None] | None = None

    def prepare(self, audio_query: AudioQuery, audio_data: bytes) -> SyncData:
        """再生準備.

        Args:
            audio_query: VOICEVOX AudioQuery
            audio_data: WAV音声データ

        Returns:
            SyncData: 同期再生用データ
        """
        # 音声読み込み
        duration = self.player.load_wav(audio_data)

        # 音素タイムライン抽出
        timeline = extract_phoneme_timeline(audio_query)

        # MouthSchedule生成
        total_duration = get_total_duration(audio_query)
        schedule = create_mouth_schedule(timeline, total_duration, self.fps)

        self._sync_data = SyncData(
            audio_query=audio_query,
            audio_data=audio_data,
            timeline=timeline,
            schedule=schedule,
            duration=duration,
        )

        return self._sync_data

    def set_viseme_callback(self, callback: Callable[[Viseme], None]) -> None:
        """Viseme更新コールバックを設定.

        Args:
            callback: Viseme更新時に呼ばれるコールバック関数
        """
        self._viseme_callback = callback

    def play(self) -> None:
        """再生開始（非ブロッキング）."""
        if self._sync_data is None:
            raise RuntimeError("No sync data prepared. Call prepare() first.")

        self.player.play(blocking=False)

    def stop(self) -> None:
        """再生停止."""
        self.player.stop()

    def get_current_viseme(self) -> Viseme:
        """現在のVisemeを取得.

        Returns:
            Viseme: 現在の口形状
        """
        if self._sync_data is None or not self.player.is_playing:
            return Viseme.CLOSED

        elapsed = self.player.elapsed_time
        return get_viseme_at_time(self._sync_data.timeline, elapsed)

    def update(self) -> Viseme:
        """フレーム更新（毎フレーム呼び出す）.

        Returns:
            Viseme: 現在の口形状
        """
        viseme = self.get_current_viseme()

        if self._viseme_callback is not None:
            self._viseme_callback(viseme)

        return viseme

    @property
    def is_playing(self) -> bool:
        """再生中かどうか."""
        return self.player.is_playing

    @property
    def elapsed_time(self) -> float:
        """経過時間（秒）."""
        return self.player.elapsed_time

    @property
    def duration(self) -> float:
        """総再生時間（秒）."""
        if self._sync_data is None:
            return 0.0
        return self._sync_data.duration

    @property
    def timeline(self) -> PhonemeTimeline | None:
        """音素タイムライン."""
        if self._sync_data is None:
            return None
        return self._sync_data.timeline

    @property
    def schedule(self) -> MouthSchedule | None:
        """MouthSchedule."""
        if self._sync_data is None:
            return None
        return self._sync_data.schedule
