"""音声再生モジュール."""

import io
import threading
import time
from dataclasses import dataclass, field

import numpy as np
import sounddevice as sd
import soundfile as sf


@dataclass
class PlaybackState:
    """再生状態."""

    is_playing: bool = False
    start_time: float = 0.0
    duration: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def elapsed_time(self) -> float:
        """経過時間（秒）."""
        if not self.is_playing:
            return 0.0
        return time.perf_counter() - self.start_time

    @property
    def is_finished(self) -> bool:
        """再生完了かどうか."""
        if not self.is_playing:
            return True
        return self.elapsed_time >= self.duration


class AudioPlayer:
    """音声再生プレイヤー."""

    def __init__(self, sample_rate: int = 24000):
        """初期化.

        Args:
            sample_rate: サンプリングレート
        """
        self.sample_rate = sample_rate
        self.state = PlaybackState()
        self._stream: sd.OutputStream | None = None
        self._audio_data: np.ndarray | None = None
        self._position: int = 0

    def load_wav(self, wav_data: bytes) -> float:
        """WAVデータを読み込み.

        Args:
            wav_data: WAV形式のバイトデータ

        Returns:
            float: 音声の長さ（秒）
        """
        with io.BytesIO(wav_data) as f:
            data, samplerate = sf.read(f, dtype="float32")

        self._audio_data = data
        self.sample_rate = samplerate
        self.state.duration = len(data) / samplerate
        self._position = 0

        return self.state.duration

    def play(self, blocking: bool = False) -> None:
        """再生開始.

        Args:
            blocking: ブロッキングモードで再生するか
        """
        if self._audio_data is None:
            raise RuntimeError("No audio data loaded")

        self.stop()
        self._position = 0

        def callback(outdata, frames, time_info, status):
            end_pos = self._position + frames
            chunk = self._audio_data[self._position : end_pos]

            if len(chunk) < frames:
                # 残りデータで埋める
                outdata[: len(chunk)] = chunk.reshape(-1, 1) if chunk.ndim == 1 else chunk
                outdata[len(chunk) :] = 0
                raise sd.CallbackStop
            else:
                outdata[:] = chunk.reshape(-1, 1) if chunk.ndim == 1 else chunk

            self._position = end_pos

        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=callback,
            finished_callback=self._on_finished,
        )

        with self.state._lock:
            self.state.is_playing = True
            self.state.start_time = time.perf_counter()

        self._stream.start()

        if blocking:
            self.wait()

    def _on_finished(self) -> None:
        """再生完了コールバック."""
        with self.state._lock:
            self.state.is_playing = False

    def stop(self) -> None:
        """再生停止."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self.state._lock:
            self.state.is_playing = False

    def wait(self) -> None:
        """再生完了まで待機."""
        while self.state.is_playing and not self.state.is_finished:
            time.sleep(0.01)
        self.stop()

    @property
    def elapsed_time(self) -> float:
        """経過時間（秒）."""
        return self.state.elapsed_time

    @property
    def is_playing(self) -> bool:
        """再生中かどうか."""
        return self.state.is_playing

    @property
    def duration(self) -> float:
        """音声の長さ（秒）."""
        return self.state.duration
